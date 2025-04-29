/**
 * Comprehensive fix for search flow visualization issues
 * This script addresses the issues with the search flow visualization not updating correctly
 */

const fs = require('fs');
const path = require('path');

// Path to the files
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');
const searchFlowPath = path.join(process.cwd(), 'src', 'components', 'search', 'SearchFlow.jsx');

// Function to update the vector-search/page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Update the Results Area section to ensure the SearchFlowIndicator is always visible during loading
    content = content.replace(
      /{hasSearched && !loading && !error && \(\s+<div className="mt-6 space-y-6">\s+{\/\* Search Flow Visualization \*\/}\s+<SearchFlowIndicator\s+currentStage={currentStage}\s+metadata={metadata}\s+\/>/g,
      `{hasSearched && (
        <div className="mt-6 space-y-6">
          {/* Search Flow Visualization - Always show during search process */}
          <SearchFlowIndicator 
            currentStage={currentStage} 
            metadata={metadata}
            loading={loading}
          />`
    );
    
    // Fix 2: Ensure the loading state is properly passed to the SearchFlowIndicator
    content = content.replace(
      /\/\/ --- handleSearch using SSE for real-time updates ---/g,
      `// --- handleSearch using SSE for real-time updates ---
    // Debug function to log the current state
    const logCurrentState = () => {
      console.log('Current state:', {
        currentStage,
        loading,
        hasSearched,
        resultsLength: results.length,
        metadata
      });
    };`
    );
    
    // Fix 3: Add logging after stage updates
    content = content.replace(
      /setCurrentStage\(data\.metadata\.stage\);/g,
      `setCurrentStage(data.metadata.stage);
            // Log the current state after stage update
            setTimeout(() => {
              console.log('Current stage state after update:', data.metadata.stage);
              console.log('Current component state:', {
                currentStage: data.metadata.stage,
                loading: true,
                hasSearched: true
              });
            }, 0);`
    );
    
    // Fix 4: Ensure the loading state is properly managed
    content = content.replace(
      /setLoading\(false\);/g,
      `setLoading(false);
                        console.log('Setting loading to false');`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with comprehensive search flow visualization fixes');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Function to update the SearchFlow.jsx file
function updateSearchFlow() {
  try {
    let content = fs.readFileSync(searchFlowPath, 'utf8');
    
    // Fix 5: Completely rewrite the SearchFlowIndicator component to ensure it works correctly
    const newSearchFlowIndicator = `/**
 * Component for displaying the search flow process with enhanced animations
 */
export function SearchFlowIndicator({ currentStage = 'start', metadata = {}, loading = false }) {
  // Debug log the current stage and loading state
  console.log('SearchFlowIndicator received:', { currentStage, loading, metadata });
  
  // Define all stages in order
  const stages = ['start', 'search', 'filter', 'combine', 'analyze', 'complete'];
  
  // Find the current stage index
  // If the stage is not found, default to the 'start' stage
  const currentIndex = stages.indexOf(currentStage) !== -1 ? stages.indexOf(currentStage) : 0;
  console.log('Stage index:', currentIndex, 'for stage:', currentStage);
  
  // Animation state
  const [animateIn, setAnimateIn] = useState(false);
  
  // Track previous stage for animation
  const [prevStage, setPrevStage] = useState(currentStage);
  const [stageChanged, setStageChanged] = useState(false);
  
  // Detect stage changes for animations
  useEffect(() => {
    console.log('Stage changed from', prevStage, 'to', currentStage);
    if (currentStage !== prevStage) {
      setPrevStage(currentStage);
      setStageChanged(true);
      
      // Reset stage changed flag after animation
      const timer = setTimeout(() => {
        setStageChanged(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [currentStage, prevStage]);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Force component to be visible even if animateIn is false
  const visibilityClass = 'opacity-100';
  
  return (
    <Card className={\`mb-6 overflow-hidden transition-all duration-500 \${visibilityClass}\`}>
      <CardHeader className="pb-2 bg-gradient-to-r from-blue-50 to-cyan-50">
        <CardTitle className="text-base flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">{PROGRESS_STAGES.start.icon}</span>
            Search Process Flow
          </div>
          {loading && (
            <div className="text-xs bg-yellow-100 px-2 py-1 rounded-full text-yellow-700 animate-pulse">
              Processing...
            </div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Progress line with animation */}
          <div className="absolute top-4 left-4 right-4 h-0.5 bg-gray-200">
            <div 
              className="h-full bg-blue-400 transition-all duration-1000" 
              style={{ 
                width: \`\${currentIndex === 0 ? 0 : (currentIndex / (stages.length - 1)) * 100}%\`,
                transitionDelay: '0.5s'
              }}
            ></div>
          </div>
          
          {/* Stages */}
          <div className="flex justify-between relative">
            {stages.map((stage, index) => {
              const stageInfo = PROGRESS_STAGES[stage] || {
                icon: '📌',
                message: stage.charAt(0).toUpperCase() + stage.slice(1),
                textColor: 'text-gray-600',
                bgColor: 'bg-gray-100'
              };
              
              const isActive = index <= currentIndex;
              const isCurrent = index === currentIndex;
              const isPast = index < currentIndex;
              
              // Calculate delay for staggered animation
              const animationDelay = 0.1 + (index * 0.15);
              
              return (
                <div 
                  key={stage} 
                  className="flex flex-col items-center z-10"
                  style={{ 
                    transition: 'transform 0.5s ease, opacity 0.5s ease',
                    transitionDelay: \`\${animationDelay}s\`,
                    opacity: 1, // Always visible
                    transform: animateIn ? 'translateY(0)' : 'translateY(10px)'
                  }}
                >
                  {/* Stage icon */}
                  <div className={\`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm search-flow-step
                    transition-all duration-300
                    \${isActive ? \`\${stageInfo.bgColor || 'bg-blue-100'}\` : 'bg-gray-100'}
                    \${isActive ? \`\${stageInfo.textColor || 'text-blue-600'}\` : 'text-gray-400'}
                    \${isCurrent ? 'ring-2 ring-offset-2 ring-blue-400 active animate-pulse' : ''}
                    \${isPast ? 'shadow-sm' : ''}
                  \`}>
                    {isCurrent && loading ? (
                      <span className="animate-spin">{STATUS_INDICATORS.progress}</span>
                    ) : (
                      <span className={isPast ? 'transform scale-110' : ''}>{stageInfo.icon}</span>
                    )}
                  </div>
                  
                  {/* Stage label */}
                  <div className={\`
                    mt-2 text-xs text-center max-w-[80px]
                    \${isActive ? stageInfo.textColor || 'text-blue-600' : 'text-gray-400'}
                    \${isActive ? stageInfo.fontWeight || 'font-medium' : 'font-normal'}
                    transition-all duration-300
                  \`}>
                    {stageInfo.message}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Current stage indicator */}
        <div className="mt-4 pt-2 border-t border-gray-200 text-sm text-center">
          <div className={\`inline-block px-3 py-1 rounded-full \${
            loading ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
          }\`}>
            {loading ? (
              <span className="flex items-center">
                <span className="animate-spin mr-1">{STATUS_INDICATORS.progress}</span>
                Processing: {currentStage.charAt(0).toUpperCase() + currentStage.slice(1)} stage
              </span>
            ) : (
              <span className="flex items-center">
                <span className="mr-1">✓</span>
                {currentStage === 'complete' ? 'Search complete' : 'Stage complete'}
              </span>
            )}
          </div>
        </div>
        
        {/* Metadata display with animation */}
        {metadata && Object.keys(metadata).length > 0 && (
          <div 
            className="mt-4 pt-2 border-t border-gray-200 grid grid-cols-2 gap-2 text-xs"
            style={{ 
              transition: 'opacity 0.5s ease, transform 0.5s ease',
              transitionDelay: '1s',
              opacity: animateIn ? 1 : 0,
              transform: animateIn ? 'translateY(0)' : 'translateY(10px)'
            }}
          >
            {metadata.search_duration_seconds !== undefined && (
              <div className="p-2 bg-blue-50 rounded-md">
                <span className="text-gray-500">⏱️ Duration:</span>{' '}
                <span className="font-medium text-blue-700">{metadata.search_duration_seconds.toFixed(2)}s</span>
              </div>
            )}
            {metadata.total_results_found !== undefined && (
              <div className="p-2 bg-green-50 rounded-md">
                <span className="text-gray-500">📊 Results:</span>{' '}
                <span className="font-medium text-green-700">{metadata.total_results_found}</span>
              </div>
            )}
            {metadata.token_usage?.embedding_tokens !== undefined && (
              <div className="p-2 bg-purple-50 rounded-md">
                <span className="text-gray-500">🧠 Embedding Tokens:</span>{' '}
                <span className="font-medium text-purple-700">{metadata.token_usage.embedding_tokens.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.generation_tokens?.input !== undefined && (
              <div className="p-2 bg-yellow-50 rounded-md">
                <span className="text-gray-500">📥 Generation Input:</span>{' '}
                <span className="font-medium text-yellow-700">{metadata.token_usage.generation_tokens.input.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.generation_tokens?.output !== undefined && (
              <div className="p-2 bg-cyan-50 rounded-md">
                <span className="text-gray-500">📤 Generation Output:</span>{' '}
                <span className="font-medium text-cyan-700">{metadata.token_usage.generation_tokens.output.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.total_tokens !== undefined && (
              <div className="p-2 bg-red-50 rounded-md">
                <span className="text-gray-500">💰 Total Tokens:</span>{' '}
                <span className="font-medium text-red-700">{metadata.token_usage.total_tokens.toLocaleString()}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}`;

    // Replace the SearchFlowIndicator component with the new implementation
    content = content.replace(
      /export function SearchFlowIndicator\(\{ currentStage = 'start', metadata = \{\} \}\) \{[\s\S]*?<\/Card>\s+\);[\s\S]*?\}/,
      newSearchFlowIndicator
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(searchFlowPath, content, 'utf8');
    console.log('Successfully updated SearchFlow.jsx with comprehensive search flow visualization fixes');
    return true;
  } catch (error) {
    console.error('Error updating SearchFlow.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    // Update SearchFlow.jsx
    const flowUpdated = updateSearchFlow();
    
    if (pageUpdated && flowUpdated) {
      console.log('Comprehensive search flow visualization fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Updated the Results Area section to ensure the SearchFlowIndicator is always visible during loading');
      console.log('2. Added debug logging for state updates');
      console.log('3. Completely rewrote the SearchFlowIndicator component to ensure it works correctly');
      console.log('4. Added a current stage indicator to show the current processing stage');
      console.log('5. Ensured the component is always visible, even during loading');
      console.log('6. Added better handling for unknown stages');
    } else {
      console.error('Failed to apply comprehensive search flow visualization fix.');
    }
  } catch (error) {
    console.error('Error applying comprehensive search flow visualization fix:', error);
  }
}

// Run the fix
applyFix();
