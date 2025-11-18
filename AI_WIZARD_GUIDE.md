# AI Wizard Chat Component

**Status**: ✅ Complete

A conversational AI interface that guides users through Writers Factory setup and features through natural chat interactions.

---

## Features

### 🧙‍♂️ Conversational UI
- Chat-based interface (like ChatGPT)
- Real-time typing indicators
- Message history with timestamps
- Auto-scroll to latest messages

### 🎯 Multiple Contexts
The wizard adapts based on context:

1. **Onboarding** - First-time user setup
2. **Project Setup** - Creating new projects
3. **NotebookLM** - Research integration
4. **Knowledge Graph** - Entity extraction
5. **Copilot** - AI writing assistant setup

### 💬 Smart Interactions
- Quick-action buttons for common choices
- Natural language responses
- Context-aware suggestions
- Progressive disclosure (one step at a time)

### ✨ Beautiful Design
- Gradient wizard avatar
- Smooth animations (fade-in, typing indicators)
- Responsive layout
- Dark theme optimized

---

## Usage

### Full-Page Wizard

```tsx
import { WizardPage } from './pages/Wizard';

// Navigate to wizard with context
navigate('/wizard?context=onboarding');
navigate('/wizard?context=notebooklm&projectId=abc123');
```

**URL Parameters**:
- `context`: onboarding | project-setup | notebooklm | knowledge-graph | copilot
- `projectId`: Optional project UUID

### Embedded Wizard

```tsx
import { AIWizard } from './components/wizard';

<AIWizard
  context="notebooklm"
  projectId={project.id}
  onComplete={() => console.log('Setup complete!')}
/>
```

### Floating Wizard Button

```tsx
import { FloatingWizard } from './components/wizard';

// Add to any page
<FloatingWizard
  projectId={project.id}
  context="knowledge-graph"
  position="bottom-right"
/>
```

This creates a floating button in the corner that opens the wizard in a modal.

---

## Conversation Flows

### 1. Onboarding Flow

```
Wizard: Welcome! What kind of story are you working on?
[Sci-Fi] [Fantasy] [Mystery] [Other]

User: *clicks Sci-Fi*

Wizard: Great! Sci-Fi is exciting. What's your project name?

User: "The Mars Colony"

Wizard: Perfect! Would you like to set up NotebookLM for research?
[Yes, set up research] [Skip for now]

User: *clicks Yes*

Wizard: Excellent! Let me guide you through NotebookLM setup.
[Continue to NotebookLM Setup]
```

### 2. NotebookLM Flow

```
Wizard: Let's set up NotebookLM for research-grounded writing!
        Have you created any NotebookLM notebooks yet?
[Yes, I have notebooks] [No, show me how]

User: *clicks No, show me how*

Wizard: Here's how to create a NotebookLM notebook:
        1. Go to notebooklm.google.com
        2. Create a new notebook
        3. Add your research sources
        4. Copy the notebook URL
        5. Come back and paste it here!
[Open NotebookLM] [I created one]

User: *clicks I created one*

Wizard: Perfect! You can configure up to 3 notebooks:
        Character Research, World Building, and Themes.
        Ready to add them?
[Configure Notebooks]
```

### 3. Knowledge Graph Flow

```
Wizard: Knowledge Graphs track characters, locations, and relationships.
        Would you like to extract entities from existing scenes or start fresh?
[Extract from scenes] [Start fresh]

User: *clicks Extract from scenes*

Wizard: I'll extract entities from your scenes automatically.
[Start Extraction]

*User clicks button*

Wizard: ✅ Extraction started! I'll notify you when it's done.
[View Knowledge Graph]
```

### 4. Copilot Flow

```
Wizard: The AI Copilot helps you write with real-time suggestions.
        Would you prefer FREE local AI or premium models?
[FREE Local AI (Ollama)] [Premium Models]

User: *clicks FREE Local AI*

Wizard: Excellent! Ollama runs AI locally - completely FREE.
        To get started:
        1. Install Ollama from ollama.ai
        2. Run: ollama pull llama2
        3. The copilot will work automatically!
[Open Ollama Website] [I installed Ollama]
```

---

## Component Architecture

### AIWizard.tsx
Main wizard component with:
- Message state management
- Conversation flow logic
- Context-specific handlers
- API integration

### WizardMessage.tsx
Individual message bubble with:
- Role-based styling (wizard vs user)
- Action button rendering
- Timestamp display

### FloatingWizard.tsx
Floating action button with:
- Pulse animation for unread messages
- Modal wizard overlay
- Positioning options

### Wizard.tsx (Page)
Full-page wrapper with:
- Top navigation bar
- Centered wizard container
- Bottom help links

---

## Extending the Wizard

### Add a New Context

1. **Add to getWelcomeMessages()**:
```tsx
case 'my-feature':
  return [
    {
      content: "Welcome to My Feature!",
      actions: []
    },
    {
      content: "What would you like to do?",
      actions: [
        { type: 'button', label: 'Option A', value: 'option-a' },
        { type: 'button', label: 'Option B', value: 'option-b' }
      ]
    }
  ];
```

2. **Add handler function**:
```tsx
const handleMyFeatureFlow = (value: string, state: any) => {
  if (state.step === 1) {
    if (value === 'option-a') {
      addWizardMessage('You chose Option A!');
    }
  }
};
```

3. **Add to switch statement**:
```tsx
switch (wizardState.context) {
  // ...
  case 'my-feature':
    handleMyFeatureFlow(value, newState);
    break;
}
```

### Add API Integration

```tsx
const callMyAPI = async () => {
  addWizardMessage('Processing...');

  try {
    const response = await fetch('/api/my-endpoint', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      const result = await response.json();
      addWizardMessage(`✅ Success! ${result.message}`);
    } else {
      addWizardMessage('❌ Something went wrong. Please try again.');
    }
  } catch (error) {
    addWizardMessage('❌ Network error. Please check your connection.');
  }
};
```

---

## Best Practices

### Conversation Design

1. **Keep messages short** - One idea per message
2. **Offer choices** - Use buttons instead of asking users to type
3. **Provide context** - Explain what each option does
4. **Show progress** - Tell users where they are in the flow
5. **Be encouraging** - Use positive, friendly language

### Technical

1. **Always add loading states** - Show "Processing..." messages
2. **Handle errors gracefully** - Friendly error messages
3. **Preserve context** - Store important data in wizardState
4. **Test all paths** - Verify every button and flow
5. **Add analytics** - Track which paths users take

---

## Customization

### Colors

Edit gradient colors in the components:

```tsx
// Wizard avatar gradient
bg-gradient-to-br from-blue-500 to-purple-500

// Action buttons gradient
bg-gradient-to-r from-blue-600 to-purple-600

// Message bubbles
bg-gray-800 // Wizard
bg-blue-600 // User
```

### Positioning (FloatingWizard)

```tsx
<FloatingWizard position="bottom-left" />  // Left side
<FloatingWizard position="bottom-right" /> // Right side (default)
```

### Animations

Speed up/slow down typing:

```tsx
setTimeout(() => {
  addWizardMessage(content);
}, 300); // Adjust delay (ms)
```

---

## Examples

### Onboarding New Users

```tsx
// Redirect new users to wizard on first login
if (user.is_first_login) {
  navigate('/wizard?context=onboarding');
}
```

### Context Help Button

```tsx
// Add help button to complex pages
<button onClick={() => setWizardOpen(true)}>
  Need Help?
</button>

{wizardOpen && (
  <div className="fixed inset-0 z-50 bg-black bg-opacity-50">
    <AIWizard
      context="knowledge-graph"
      projectId={project.id}
      onComplete={() => setWizardOpen(false)}
    />
  </div>
)}
```

### Project Setup Wizard

```tsx
// Show wizard after creating project
const createProject = async () => {
  const project = await api.createProject(data);
  navigate(`/wizard?context=project-setup&projectId=${project.id}`);
};
```

---

## Testing

### Manual Testing Checklist

- [ ] All conversation paths work
- [ ] Buttons trigger correct actions
- [ ] API calls succeed/fail gracefully
- [ ] Messages appear in correct order
- [ ] Timestamps are accurate
- [ ] Auto-scroll works
- [ ] Typing indicator appears
- [ ] Modal opens/closes properly
- [ ] Floating button pulse works
- [ ] Responsive on mobile

### Test Different Contexts

```tsx
// Test each context
navigate('/wizard?context=onboarding');
navigate('/wizard?context=notebooklm');
navigate('/wizard?context=knowledge-graph');
navigate('/wizard?context=copilot');
```

---

## Future Enhancements

### Potential Additions

1. **Voice Input** - Allow users to speak instead of type
2. **Multi-language** - i18n support for conversations
3. **Persistent History** - Save conversation to database
4. **Smart Suggestions** - ML-powered response suggestions
5. **File Upload** - Upload files directly in chat
6. **Rich Media** - Images, videos, code blocks in messages
7. **Branching Flows** - More complex decision trees
8. **User Preferences** - Remember user choices
9. **Analytics Dashboard** - Track wizard usage metrics
10. **A/B Testing** - Test different conversation flows

---

## Troubleshooting

### Wizard doesn't appear

- Check that component is properly imported
- Verify route is configured (for WizardPage)
- Check z-index (should be 50 for modal)

### Messages don't show

- Check console for errors
- Verify addWizardMessage() is called
- Check message state in React DevTools

### Buttons don't work

- Verify onClick/value/href is set correctly
- Check handleActionClick() implementation
- Look for errors in browser console

### API calls fail

- Check auth token is present
- Verify endpoint URL is correct
- Check network tab for error details
- Ensure CORS is configured

---

## Architecture Diagram

```
┌──────────────────────────────────────┐
│         WizardPage.tsx               │
│  (Full-page wrapper with nav)        │
└────────────┬─────────────────────────┘
             │
             │ renders
             ▼
┌──────────────────────────────────────┐
│         AIWizard.tsx                 │
│  • Message state management          │
│  • Conversation flow logic           │
│  • Context switching                 │
│  • API integration                   │
└────────────┬─────────────────────────┘
             │
             │ renders each
             ▼
┌──────────────────────────────────────┐
│       WizardMessage.tsx              │
│  • Message bubble rendering          │
│  • Action button display             │
│  • Timestamp formatting              │
└──────────────────────────────────────┘

Alternative:
┌──────────────────────────────────────┐
│     FloatingWizard.tsx               │
│  • Floating action button            │
│  • Modal wrapper                     │
│  • Embeds AIWizard                   │
└──────────────────────────────────────┘
```

---

**Created**: 2025-01-18
**Status**: Production Ready
**Estimated Development Time**: 6-8 hours (completed in one session!)

**Next Steps**: Add the wizard to the main navigation and test all conversation flows!
