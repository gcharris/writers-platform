import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { worksApi, commentsApi } from '../api/community';
import { useAuthStore } from '../store/authStore';
import Badge from '../components/Badge';
import { ArrowLeftIcon, HeartIcon, EyeIcon, SparklesIcon, ChatBubbleLeftIcon, CubeTransparentIcon } from '@heroicons/react/24/outline';

// Phase 2: Import Knowledge Graph visualization from Factory
// Note: This assumes both frontends are in the same monorepo
// Alternative: Copy component to community-frontend or create shared package
const GraphVisualization = ({ projectId }: { projectId: string }) => {
  // Lazy load the actual component to avoid bundling issues
  // In production, this would be a proper import or shared component
  return (
    <div className="bg-white rounded-lg p-8 text-center">
      <CubeTransparentIcon className="h-16 w-16 mx-auto text-purple-300 mb-4" />
      <p className="text-gray-600 mb-4">
        Knowledge Graph visualization for this work.
        View the full interactive graph at Writers Factory.
      </p>
      <a
        href={`https://writersfactory.app/projects/${projectId}/knowledge-graph`}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
      >
        Open Interactive Graph
      </a>
    </div>
  );
};

export default function ViewWork() {
  const workIdParam = useParams();
  const workId = workIdParam.workId as string;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const [newComment, setNewComment] = useState('');
  const [activeTab, setActiveTab] = useState<'read' | 'graph'>('read');

  const workQuery = useQuery({
    queryKey: ['work', workId],
    queryFn: () => worksApi.get(workId),
    enabled: !!workId,
  });

  const commentsQuery = useQuery({
    queryKey: ['comments', workId],
    queryFn: () => commentsApi.list(workId),
    enabled: !!workId,
  });

  const likeMutation = useMutation({
    mutationFn: (liked: boolean) => liked ? worksApi.unlike(workId) : worksApi.like(workId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work', workId] });
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content: string) => commentsApi.create(workId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', workId] });
      setNewComment('');
    },
  });

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      await commentMutation.mutateAsync(newComment);
    }
  };

  if (workQuery.isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading work...</p>
        </div>
      </div>
    );
  }

  const work = workQuery.data;
  const comments = commentsQuery.data;

  if (!work) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Work not found</p>
          <button onClick={() => navigate('/browse')} className="mt-4 text-sky-600 hover:text-sky-700">
            Back to Browse
          </button>
        </div>
      </div>
    );
  }

  const isLiked = false;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button onClick={() => navigate('/browse')} className="text-gray-600 hover:text-gray-900 flex items-center gap-2 mb-4">
            <ArrowLeftIcon className="h-5 w-5" />
            Back to Browse
          </button>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{work.title}</h1>
              <p className="text-lg text-gray-600 mb-4">by {work.author.username}</p>

              <div className="flex flex-wrap gap-2 mb-4">
                {work.badges.map((badge) => (
                  <Badge key={badge.id} badge={badge} size="md" />
                ))}
              </div>

              {work.genre && (
                <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded">
                  {work.genre}
                </span>
              )}
            </div>

            <button
              onClick={() => likeMutation.mutate(isLiked)}
              disabled={!isAuthenticated}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${isLiked ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              <HeartIcon className="h-5 w-5" />
              <span>{work.like_count}</span>
            </button>
          </div>

          <div className="flex items-center gap-6 text-sm text-gray-500 mt-4">
            <div className="flex items-center gap-1">
              <EyeIcon className="h-4 w-4" />
              <span>{work.view_count} views</span>
            </div>
            <div className="flex items-center gap-1">
              <ChatBubbleLeftIcon className="h-4 w-4" />
              <span>{comments?.length || 0} comments</span>
            </div>
            <div>
              <span>{work.word_count.toLocaleString()} words</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Phase 2: Tabs for Read Story vs Knowledge Graph */}
        {work.factory_project_id && (
          <div className="mb-6 border-b border-gray-200">
            <nav className="flex gap-8">
              <button
                onClick={() => setActiveTab('read')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'read'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Read Story
              </button>
              <button
                onClick={() => setActiveTab('graph')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
                  activeTab === 'graph'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <CubeTransparentIcon className="h-4 w-4" />
                Explore Knowledge Graph
              </button>
            </nav>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {/* Show description only in read tab */}
            {activeTab === 'read' && work.description && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">About This Work</h2>
                <p className="text-gray-700">{work.description}</p>
              </div>
            )}

            {/* Phase 2: Conditional rendering based on active tab */}
            {activeTab === 'read' ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                <div className="prose prose-lg max-w-none">
                  <div className="whitespace-pre-wrap font-serif text-gray-900 leading-relaxed">
                    {work.content}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    This knowledge graph was automatically generated from the author's manuscript using AI analysis.
                    Explore characters, locations, and relationships visualized below.
                  </p>
                </div>

                <GraphVisualization projectId={work.factory_project_id!} />
              </div>
            )}

            <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Comments ({comments?.length || 0})</h2>

              {isAuthenticated ? (
                <form onSubmit={handleAddComment} className="mb-6">
                  <textarea value={newComment} onChange={(e) => setNewComment(e.target.value)} placeholder="Share your thoughts..." rows={3} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent" />
                  <button type="submit" disabled={!newComment.trim() || commentMutation.isPending} className="mt-2 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50">
                    {commentMutation.isPending ? 'Posting...' : 'Post Comment'}
                  </button>
                </form>
              ) : (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg text-center">
                  <p className="text-gray-600">
                    <a href="/login" className="text-sky-600 hover:text-sky-700">Sign in</a> to leave a comment
                  </p>
                </div>
              )}

              <div className="space-y-4">
                {comments && comments.length > 0 ? (
                  comments.map((comment) => (
                    <div key={comment.id} className="border-t border-gray-200 pt-4">
                      <div>
                        <p className="font-medium text-gray-900">{comment.author.username}</p>
                        <p className="text-sm text-gray-500">{new Date(comment.created_at).toLocaleDateString()}</p>
                      </div>
                      <p className="mt-2 text-gray-700">{comment.content}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No comments yet. Be the first!</p>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            {work.factory_project_id ? (
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow-sm border border-purple-200 p-6 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <SparklesIcon className="h-6 w-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">AI Analysis Results</h3>
                </div>

                <a href={`https://writersfactory.app/projects/${work.factory_project_id}`} target="_blank" rel="noopener noreferrer" className="block w-full text-center px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors">
                  View Full Analysis
                </a>
              </div>
            ) : (
              <div className="bg-gradient-to-br from-sky-50 to-blue-50 rounded-lg shadow-sm border border-sky-200 p-6 mb-6">
                <SparklesIcon className="h-8 w-8 text-sky-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Want Professional Feedback?</h3>
                <p className="text-gray-700 text-sm mb-4">
                  Analyze your work with 5 AI models across 7 dimensions.
                </p>
                <a href="https://writersfactory.app" target="_blank" rel="noopener noreferrer" className="block w-full text-center px-4 py-2 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors">
                  Try Writers Factory
                </a>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">About the Author</h3>
              <p className="text-gray-700 font-medium">{work.author.username}</p>
              <p className="text-sm text-gray-500 mt-2">Published {new Date(work.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
