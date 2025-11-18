/**
 * Professional Markdown Editor with Tiptap
 *
 * Features:
 * - WYSIWYG + Markdown toggle view
 * - Full formatting toolbar
 * - Markdown import/export
 * - AI Copilot integration
 * - Focus mode
 * - Auto-save
 * - Word count
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import {
  Bars3Icon,
  BoldIcon,
  ItalicIcon,
  ListBulletIcon,
  CodeBracketIcon,
  LinkIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

interface MarkdownEditorProps {
  content: string;
  onChange: (content: string) => void;
  onSave?: () => void;
  placeholder?: string;
  className?: string;
  autoSave?: boolean;
  autoSaveDelay?: number;
  copilotEnabled?: boolean;
  projectId?: string;
  sceneId?: string;
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  content,
  onChange,
  onSave,
  placeholder = 'Start writing your story...',
  className = '',
  autoSave = true,
  autoSaveDelay = 2000,
  copilotEnabled = false,
  projectId,
  sceneId,
}) => {
  const [viewMode, setViewMode] = useState<'wysiwyg' | 'markdown'>('wysiwyg');
  const [markdownSource, setMarkdownSource] = useState('');
  const [focusMode, setFocusMode] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [showCopilot, setShowCopilot] = useState(false);

  // Initialize Tiptap editor
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
      }),
      Placeholder.configure({
        placeholder,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 underline hover:text-blue-800',
        },
      }),
    ],
    content,
    editorProps: {
      attributes: {
        class: 'prose prose-lg max-w-none focus:outline-none min-h-[500px] px-8 py-6',
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const markdown = htmlToMarkdown(html);
      onChange(markdown);
      setMarkdownSource(markdown);

      // Update word count
      const text = editor.getText();
      const words = text.split(/\s+/).filter(Boolean).length;
      setWordCount(words);
    },
  });

  // Convert HTML to Markdown (simple conversion)
  const htmlToMarkdown = (html: string): string => {
    let markdown = html;

    // Headings
    markdown = markdown.replace(/<h1>(.*?)<\/h1>/g, '# $1\n');
    markdown = markdown.replace(/<h2>(.*?)<\/h2>/g, '## $1\n');
    markdown = markdown.replace(/<h3>(.*?)<\/h3>/g, '### $1\n');
    markdown = markdown.replace(/<h4>(.*?)<\/h4>/g, '#### $1\n');
    markdown = markdown.replace(/<h5>(.*?)<\/h5>/g, '##### $1\n');
    markdown = markdown.replace(/<h6>(.*?)<\/h6>/g, '###### $1\n');

    // Bold and Italic
    markdown = markdown.replace(/<strong>(.*?)<\/strong>/g, '**$1**');
    markdown = markdown.replace(/<em>(.*?)<\/em>/g, '*$1*');
    markdown = markdown.replace(/<s>(.*?)<\/s>/g, '~~$1~~');

    // Code
    markdown = markdown.replace(/<code>(.*?)<\/code>/g, '`$1`');
    markdown = markdown.replace(/<pre><code>(.*?)<\/code><\/pre>/gs, '```\n$1\n```');

    // Links
    markdown = markdown.replace(/<a href="(.*?)".*?>(.*?)<\/a>/g, '[$2]($1)');

    // Lists
    markdown = markdown.replace(/<ul>(.*?)<\/ul>/gs, (match, content) => {
      return content.replace(/<li>(.*?)<\/li>/g, '- $1\n');
    });
    markdown = markdown.replace(/<ol>(.*?)<\/ol>/gs, (match, content) => {
      let index = 1;
      return content.replace(/<li>(.*?)<\/li>/g, () => `${index++}. $1\n`);
    });

    // Blockquotes
    markdown = markdown.replace(/<blockquote>(.*?)<\/blockquote>/gs, (match, content) => {
      return '> ' + content.replace(/<p>(.*?)<\/p>/g, '$1\n> ').trim() + '\n';
    });

    // Paragraphs
    markdown = markdown.replace(/<p>(.*?)<\/p>/g, '$1\n\n');

    // Horizontal rule
    markdown = markdown.replace(/<hr\s*\/?>/g, '---\n');

    // Clean up HTML tags
    markdown = markdown.replace(/<[^>]+>/g, '');
    markdown = markdown.replace(/&nbsp;/g, ' ');
    markdown = markdown.replace(/&amp;/g, '&');
    markdown = markdown.replace(/&lt;/g, '<');
    markdown = markdown.replace(/&gt;/g, '>');

    return markdown.trim();
  };

  // Convert Markdown to HTML for Tiptap
  const markdownToHtml = (markdown: string): string => {
    let html = markdown;

    // Headings
    html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
    html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

    // Bold and Italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/~~(.+?)~~/g, '<s>$1</s>');

    // Code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');

    // Links
    html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');

    // Lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

    // Blockquotes
    html = html.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>');

    // Paragraphs
    html = html.replace(/^(?!<[hul]|<blockquote|<pre)(.+)$/gm, '<p>$1</p>');

    // Horizontal rule
    html = html.replace(/^---$/gm, '<hr>');

    return html;
  };

  // Toggle between WYSIWYG and Markdown
  const toggleViewMode = () => {
    if (viewMode === 'wysiwyg') {
      // Switch to markdown
      const markdown = htmlToMarkdown(editor?.getHTML() || '');
      setMarkdownSource(markdown);
      setViewMode('markdown');
    } else {
      // Switch to WYSIWYG
      const html = markdownToHtml(markdownSource);
      editor?.commands.setContent(html);
      setViewMode('wysiwyg');
    }
  };

  // Handle markdown source changes
  const handleMarkdownChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newMarkdown = e.target.value;
    setMarkdownSource(newMarkdown);
    onChange(newMarkdown);

    // Update word count
    const words = newMarkdown.split(/\s+/).filter(Boolean).length;
    setWordCount(words);
  };

  // Toolbar actions
  const toggleBold = () => editor?.chain().focus().toggleBold().run();
  const toggleItalic = () => editor?.chain().focus().toggleItalic().run();
  const toggleStrike = () => editor?.chain().focus().toggleStrike().run();
  const toggleCode = () => editor?.chain().focus().toggleCode().run();
  const toggleBlockquote = () => editor?.chain().focus().toggleBlockquote().run();
  const toggleBulletList = () => editor?.chain().focus().toggleBulletList().run();
  const toggleOrderedList = () => editor?.chain().focus().toggleOrderedList().run();
  const toggleCodeBlock = () => editor?.chain().focus().toggleCodeBlock().run();
  const setHeading = (level: 1 | 2 | 3 | 4 | 5 | 6) =>
    editor?.chain().focus().toggleHeading({ level }).run();

  const addLink = () => {
    const url = window.prompt('Enter URL:');
    if (url) {
      editor?.chain().focus().setLink({ href: url }).run();
    }
  };

  // Export to markdown file
  const exportMarkdown = () => {
    const markdown = viewMode === 'markdown' ? markdownSource : htmlToMarkdown(editor?.getHTML() || '');
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scene-${sceneId || 'export'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Import from markdown file
  const importMarkdown = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.md,.markdown,.txt';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const markdown = event.target?.result as string;
          setMarkdownSource(markdown);
          if (viewMode === 'wysiwyg') {
            const html = markdownToHtml(markdown);
            editor?.commands.setContent(html);
          }
          onChange(markdown);
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  // Auto-save effect
  useEffect(() => {
    if (!autoSave || !onSave) return;

    const timer = setTimeout(() => {
      onSave();
    }, autoSaveDelay);

    return () => clearTimeout(timer);
  }, [content, autoSave, autoSaveDelay, onSave]);

  // Initialize markdown source
  useEffect(() => {
    if (editor && content) {
      const markdown = htmlToMarkdown(editor.getHTML());
      setMarkdownSource(markdown);
    }
  }, [editor]);

  if (!editor) {
    return <div className="p-8 text-center text-gray-500">Loading editor...</div>;
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Toolbar */}
      <div className={`bg-white border-b border-gray-200 ${focusMode ? 'hidden' : 'block'}`}>
        <div className="flex items-center justify-between px-4 py-2">
          {/* Formatting Tools */}
          <div className="flex items-center gap-1">
            {/* Headings */}
            <div className="flex items-center gap-1 border-r border-gray-300 pr-2 mr-2">
              <button
                onClick={() => setHeading(1)}
                className={`p-2 rounded hover:bg-gray-100 text-sm font-bold ${
                  editor.isActive('heading', { level: 1 }) ? 'bg-gray-200' : ''
                }`}
                title="Heading 1"
              >
                H1
              </button>
              <button
                onClick={() => setHeading(2)}
                className={`p-2 rounded hover:bg-gray-100 text-sm font-bold ${
                  editor.isActive('heading', { level: 2 }) ? 'bg-gray-200' : ''
                }`}
                title="Heading 2"
              >
                H2
              </button>
              <button
                onClick={() => setHeading(3)}
                className={`p-2 rounded hover:bg-gray-100 text-sm font-bold ${
                  editor.isActive('heading', { level: 3 }) ? 'bg-gray-200' : ''
                }`}
                title="Heading 3"
              >
                H3
              </button>
            </div>

            {/* Text Formatting */}
            <button
              onClick={toggleBold}
              className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('bold') ? 'bg-gray-200' : ''}`}
              title="Bold (Ctrl+B)"
            >
              <BoldIcon className="h-4 w-4" />
            </button>
            <button
              onClick={toggleItalic}
              className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('italic') ? 'bg-gray-200' : ''}`}
              title="Italic (Ctrl+I)"
            >
              <ItalicIcon className="h-4 w-4" />
            </button>
            <button
              onClick={toggleStrike}
              className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('strike') ? 'bg-gray-200' : ''}`}
              title="Strikethrough"
            >
              <span className="text-sm font-bold line-through">S</span>
            </button>
            <button
              onClick={toggleCode}
              className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('code') ? 'bg-gray-200' : ''}`}
              title="Inline Code"
            >
              <CodeBracketIcon className="h-4 w-4" />
            </button>

            {/* Lists */}
            <div className="flex items-center gap-1 border-l border-gray-300 pl-2 ml-2">
              <button
                onClick={toggleBulletList}
                className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('bulletList') ? 'bg-gray-200' : ''}`}
                title="Bullet List"
              >
                <ListBulletIcon className="h-4 w-4" />
              </button>
              <button
                onClick={toggleOrderedList}
                className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('orderedList') ? 'bg-gray-200' : ''}`}
                title="Numbered List"
              >
                <Bars3Icon className="h-4 w-4" />
              </button>
            </div>

            {/* Other */}
            <div className="flex items-center gap-1 border-l border-gray-300 pl-2 ml-2">
              <button
                onClick={toggleBlockquote}
                className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('blockquote') ? 'bg-gray-200' : ''}`}
                title="Quote"
              >
                <span className="text-sm font-bold">"</span>
              </button>
              <button
                onClick={toggleCodeBlock}
                className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('codeBlock') ? 'bg-gray-200' : ''}`}
                title="Code Block"
              >
                <span className="text-xs font-mono">{'</>'}</span>
              </button>
              <button
                onClick={addLink}
                className={`p-2 rounded hover:bg-gray-100 ${editor.isActive('link') ? 'bg-gray-200' : ''}`}
                title="Add Link"
              >
                <LinkIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            {/* Word Count */}
            <span className="text-sm text-gray-500">
              {wordCount.toLocaleString()} words
            </span>

            {/* View Mode Toggle */}
            <button
              onClick={toggleViewMode}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
            >
              {viewMode === 'wysiwyg' ? 'Show Markdown' : 'Show WYSIWYG'}
            </button>

            {/* Import/Export */}
            <div className="flex gap-1 border-l border-gray-300 pl-2">
              <button
                onClick={importMarkdown}
                className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded"
                title="Import Markdown"
              >
                Import
              </button>
              <button
                onClick={exportMarkdown}
                className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded"
                title="Export Markdown"
              >
                Export
              </button>
            </div>

            {/* Focus Mode */}
            <button
              onClick={() => setFocusMode(!focusMode)}
              className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded"
              title="Focus Mode (Hide Toolbar)"
            >
              {focusMode ? 'Exit Focus' : 'Focus'}
            </button>

            {/* AI Copilot Toggle */}
            {copilotEnabled && (
              <button
                onClick={() => setShowCopilot(!showCopilot)}
                className={`px-3 py-1 text-sm rounded flex items-center gap-1 ${
                  showCopilot ? 'bg-purple-100 text-purple-700' : 'text-gray-700 hover:bg-gray-100'
                }`}
                title="Toggle AI Copilot"
              >
                <SparklesIcon className="h-4 w-4" />
                Copilot
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 overflow-hidden flex">
        {/* Main Editor */}
        <div className={`flex-1 overflow-y-auto ${showCopilot ? 'w-2/3' : 'w-full'}`}>
          {viewMode === 'wysiwyg' ? (
            <EditorContent editor={editor} className="h-full" />
          ) : (
            <textarea
              value={markdownSource}
              onChange={handleMarkdownChange}
              className="w-full h-full p-8 font-mono text-sm resize-none focus:outline-none"
              placeholder="# Start writing in markdown..."
            />
          )}
        </div>

        {/* AI Copilot Sidebar */}
        {showCopilot && copilotEnabled && (
          <div className="w-1/3 border-l border-gray-200 bg-gray-50 p-4 overflow-y-auto">
            <div className="flex items-center gap-2 mb-4">
              <SparklesIcon className="h-5 w-5 text-purple-600" />
              <h3 className="font-semibold text-gray-900">AI Copilot</h3>
            </div>
            <p className="text-sm text-gray-600">
              AI suggestions will appear here as you write...
            </p>
            {/* TODO: Integrate with existing CopilotEditor functionality */}
          </div>
        )}
      </div>

      {/* Focus Mode Overlay Controls */}
      {focusMode && (
        <button
          onClick={() => setFocusMode(false)}
          className="fixed bottom-4 right-4 px-4 py-2 bg-gray-900 text-white rounded-lg shadow-lg hover:bg-gray-800"
        >
          Exit Focus Mode
        </button>
      )}
    </div>
  );
};

export default MarkdownEditor;
