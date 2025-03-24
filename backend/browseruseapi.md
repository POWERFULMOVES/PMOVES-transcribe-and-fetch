🌐 Browser Use WebUI
Control your browser with AI assistance
⚙️ Agent Settings
🔧 LLM Configuration
🌐 Browser Settings
🤖 Run Agent
🧐 Deep Research
📊 Results
🎥 Recordings
📁 Configuration
⚙️ Agent Settings
🔧 LLM Configuration
🌐 Browser Settings
🤖 Run Agent
🧐 Deep Research
📊 Results
🎥 Recordings
📁 Configuration
Agent Type
Select the type of agent to use

org
custom
Max Run Steps
Maximum number of steps the agent will take

100
↺
1

200
Max Actions per Step
Maximum number of actions the agent will take per step

10
↺
1

20
Enable visual processing capabilities

Use Vision
Use via APIlogo
 ·
Built with Gradiologo

·  
SettingsSettings

API documentation
http://localhost:7788/

API Recorder

11 API endpoints


Choose a language to see the code snippets for interacting with the API.

1. Install the python client (docs) if you don't already have it installed.

copy
$ pip install gradio_client
2. Find the API endpoint below corresponding to your desired function in the app. Copy the code snippet, replacing the placeholder values with your own input data. Or use the 
API Recorder

 to automatically generate your API requests.

api_name: /stop_agent
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		api_name="/stop_agent"
)
print(result)
Accepts 0 parameters:
Returns 1 element
str

The output value that appears in the "Errors" Textbox component.

api_name: /run_with_stream
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		agent_type="custom",
		llm_provider="openai",
		llm_model_name="gpt-4o",
		llm_temperature=1,
		llm_base_url="",
		llm_api_key="",
		use_own_browser=True,
		keep_browser_open=False,
		headless=False,
		disable_security=True,
		window_w=1280,
		window_h=1100,
		save_recording_path="./tmp/record_videos",
		save_agent_history_path="./tmp/agent_history",
		save_trace_path="./tmp/traces",
		enable_recording=True,
		task="go to google.com and type 'OpenAI' click search and give me the first url",
		add_infos="Hello!!",
		max_steps=100,
		use_vision=True,
		max_actions_per_step=10,
		tool_calling_method="auto",
		api_name="/run_with_stream"
)
print(result)
Accepts 22 parameters:
agent_type Literal['org', 'custom'] Default: "custom"

The input value that is provided in the "Agent Type" Radio component.

llm_provider Literal['anthropic', 'openai', 'deepseek', 'google', 'ollama', 'azure_openai', 'mistral'] Default: "openai"

The input value that is provided in the "LLM Provider" Dropdown component.

llm_model_name Literal['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o3-mini'] Default: "gpt-4o"

The input value that is provided in the "Model Name" Dropdown component.

llm_temperature float Default: 1

The input value that is provided in the "Temperature" Slider component.

llm_base_url str Default: ""

The input value that is provided in the "Base URL" Textbox component.

llm_api_key str Default: ""

The input value that is provided in the "API Key" Textbox component.

use_own_browser bool Default: True

The input value that is provided in the "Use Own Browser" Checkbox component.

keep_browser_open bool Default: False

The input value that is provided in the "Keep Browser Open" Checkbox component.

headless bool Default: False

The input value that is provided in the "Headless Mode" Checkbox component.

disable_security bool Default: True

The input value that is provided in the "Disable Security" Checkbox component.

window_w float Default: 1280

The input value that is provided in the "Window Width" Number component.

window_h float Default: 1100

The input value that is provided in the "Window Height" Number component.

save_recording_path str Default: "./tmp/record_videos"

The input value that is provided in the "Recording Path" Textbox component.

save_agent_history_path str Default: "./tmp/agent_history"

The input value that is provided in the "Agent History Save Path" Textbox component.

save_trace_path str Default: "./tmp/traces"

The input value that is provided in the "Trace Path" Textbox component.

enable_recording bool Default: True

The input value that is provided in the "Enable Recording" Checkbox component.

task str Default: "go to google.com and type 'OpenAI' click search and give me the first url"

The input value that is provided in the "Task Description" Textbox component.

add_infos str Required

The input value that is provided in the "Additional Information" Textbox component.

max_steps float Default: 100

The input value that is provided in the "Max Run Steps" Slider component.

use_vision bool Default: True

The input value that is provided in the "Use Vision" Checkbox component.

max_actions_per_step float Default: 10

The input value that is provided in the "Max Actions per Step" Slider component.

tool_calling_method Literal['auto', 'json_schema', 'function_calling'] Default: "auto"

The input value that is provided in the "Tool Calling Method" Dropdown component.

Returns tuple of 8 elements
[0] str

The output value that appears in the "Live Browser View" Html component.

[1] str

The output value that appears in the "Final Result" Textbox component.

[2] str

The output value that appears in the "Errors" Textbox component.

[3] str

The output value that appears in the "Model Actions" Textbox component.

[4] str

The output value that appears in the "Model Thoughts" Textbox component.

[5] dict(video: filepath, subtitles: filepath | None)

The output value that appears in the "Latest Recording" Video component.

[6] filepath

The output value that appears in the "Trace File" File component.

[7] filepath

The output value that appears in the "Agent History" File component.

api_name: /run_deep_search
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		research_task="Compose a report on the use of Reinforcement Learning for training Large Language Models, encompassing its origins, current advancements, and future prospects, substantiated with examples of relevant models and techniques. The report should reflect original insights and analysis, moving beyond mere summarization of existing literature.",
		max_search_iteration_input=20,
		max_query_per_iter_input=5,
		llm_provider="openai",
		llm_model_name="gpt-4o",
		llm_temperature=1,
		llm_base_url="",
		llm_api_key="",
		use_vision=True,
		use_own_browser=True,
		headless=False,
		api_name="/run_deep_search"
)
print(result)
Accepts 11 parameters:
research_task str Default: "Compose a report on the use of Reinforcement Learning for training Large Language Models, encompassing its origins, current advancements, and future prospects, substantiated with examples of relevant models and techniques. The report should reflect original insights and analysis, moving beyond mere summarization of existing literature."

The input value that is provided in the "Research Task" Textbox component.

max_search_iteration_input float Default: 20

The input value that is provided in the "Max Search Iteration" Number component.

max_query_per_iter_input float Default: 5

The input value that is provided in the "Max Query per Iteration" Number component.

llm_provider Literal['anthropic', 'openai', 'deepseek', 'google', 'ollama', 'azure_openai', 'mistral'] Default: "openai"

The input value that is provided in the "LLM Provider" Dropdown component.

llm_model_name Literal['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o3-mini'] Default: "gpt-4o"

The input value that is provided in the "Model Name" Dropdown component.

llm_temperature float Default: 1

The input value that is provided in the "Temperature" Slider component.

llm_base_url str Default: ""

The input value that is provided in the "Base URL" Textbox component.

llm_api_key str Default: ""

The input value that is provided in the "API Key" Textbox component.

use_vision bool Default: True

The input value that is provided in the "Use Vision" Checkbox component.

use_own_browser bool Default: True

The input value that is provided in the "Use Own Browser" Checkbox component.

headless bool Default: False

The input value that is provided in the "Headless Mode" Checkbox component.

Returns tuple of 2 elements
[0] str

The output value that appears in the "Research Report" Markdown component.

[1] filepath

The output value that appears in the "Download Research Report" File component.

api_name: /stop_research_agent
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		api_name="/stop_research_agent"
)
print(result)
Accepts 0 parameters:
Returns 1 element
api_name: /list_recordings
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		save_recording_path="./tmp/record_videos",
		api_name="/list_recordings"
)
print(result)
Accepts 1 parameter:
save_recording_path str Default: "./tmp/record_videos"

The input value that is provided in the "Recording Path" Textbox component.

Returns 1 element
list[dict(image: dict(path: str | None (Path to a local file), url: str | None (Publicly available url or base64 encoded image), size: int | None (Size of image in bytes), orig_name: str | None (Original filename), mime_type: str | None (mime type of image), is_stream: bool (Can always be set to False), meta: dict()), caption: str | None) | dict(video: filepath, caption: str | None)]

The output value that appears in the "Recordings" Gallery component.

api_name: /update_ui_from_config
copy
from gradio_client import Client, handle_file

client = Client("http://localhost:7788/")
result = client.predict(
		config_file=handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf'),
		api_name="/update_ui_from_config"
)
print(result)
Accepts 1 parameter:
config_file filepath Required

The input value that is provided in the "Load Config File" File component. The FileData class is a subclass of the GradioModel class that represents a file object within a Gradio interface. It is used to store file data and metadata when a file is uploaded. Attributes: path: The server file path where the file is stored. url: The normalized server URL pointing to the file. size: The size of the file in bytes. orig_name: The original filename before upload. mime_type: The MIME type of the file. is_stream: Indicates whether the file is a stream. meta: Additional metadata used internally (should not be changed).

Returns tuple of 22 elements
[0] Literal['org', 'custom']

The output value that appears in the "Agent Type" Radio component.

[1] float

The output value that appears in the "Max Run Steps" Slider component.

[2] float

The output value that appears in the "Max Actions per Step" Slider component.

[3] bool

The output value that appears in the "Use Vision" Checkbox component.

[4] Literal['auto', 'json_schema', 'function_calling']

The output value that appears in the "Tool Calling Method" Dropdown component.

[5] Literal['anthropic', 'openai', 'deepseek', 'google', 'ollama', 'azure_openai', 'mistral']

The output value that appears in the "LLM Provider" Dropdown component.

[6] Literal['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o3-mini']

The output value that appears in the "Model Name" Dropdown component.

[7] float

The output value that appears in the "Temperature" Slider component.

[8] str

The output value that appears in the "Base URL" Textbox component.

[9] str

The output value that appears in the "API Key" Textbox component.

[10] bool

The output value that appears in the "Use Own Browser" Checkbox component.

[11] bool

The output value that appears in the "Keep Browser Open" Checkbox component.

[12] bool

The output value that appears in the "Headless Mode" Checkbox component.

[13] bool

The output value that appears in the "Disable Security" Checkbox component.

[14] bool

The output value that appears in the "Enable Recording" Checkbox component.

[15] float

The output value that appears in the "Window Width" Number component.

[16] float

The output value that appears in the "Window Height" Number component.

[17] str

The output value that appears in the "Recording Path" Textbox component.

[18] str

The output value that appears in the "Trace Path" Textbox component.

[19] str

The output value that appears in the "Agent History Save Path" Textbox component.

[20] str

The output value that appears in the "Task Description" Textbox component.

[21] str

The output value that appears in the "Status" Textbox component.

api_name: /save_current_config
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		param_0="custom",
		param_1=100,
		param_2=10,
		param_3=True,
		param_4="auto",
		param_5="openai",
		param_6="gpt-4o",
		param_7=1,
		param_8="",
		param_9="",
		param_10=True,
		param_11=False,
		param_12=False,
		param_13=True,
		param_14=True,
		param_15=1280,
		param_16=1100,
		param_17="./tmp/record_videos",
		param_18="./tmp/traces",
		param_19="./tmp/agent_history",
		param_20="go to google.com and type 'OpenAI' click search and give me the first url",
		api_name="/save_current_config"
)
print(result)
Accepts 21 parameters:
param_0 Literal['org', 'custom'] Default: "custom"

The input value that is provided in the "Agent Type" Radio component.

param_1 float Default: 100

The input value that is provided in the "Max Run Steps" Slider component.

param_2 float Default: 10

The input value that is provided in the "Max Actions per Step" Slider component.

param_3 bool Default: True

The input value that is provided in the "Use Vision" Checkbox component.

param_4 Literal['auto', 'json_schema', 'function_calling'] Default: "auto"

The input value that is provided in the "Tool Calling Method" Dropdown component.

param_5 Literal['anthropic', 'openai', 'deepseek', 'google', 'ollama', 'azure_openai', 'mistral'] Default: "openai"

The input value that is provided in the "LLM Provider" Dropdown component.

param_6 Literal['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o3-mini'] Default: "gpt-4o"

The input value that is provided in the "Model Name" Dropdown component.

param_7 float Default: 1

The input value that is provided in the "Temperature" Slider component.

param_8 str Default: ""

The input value that is provided in the "Base URL" Textbox component.

param_9 str Default: ""

The input value that is provided in the "API Key" Textbox component.

param_10 bool Default: True

The input value that is provided in the "Use Own Browser" Checkbox component.

param_11 bool Default: False

The input value that is provided in the "Keep Browser Open" Checkbox component.

param_12 bool Default: False

The input value that is provided in the "Headless Mode" Checkbox component.

param_13 bool Default: True

The input value that is provided in the "Disable Security" Checkbox component.

param_14 bool Default: True

The input value that is provided in the "Enable Recording" Checkbox component.

param_15 float Default: 1280

The input value that is provided in the "Window Width" Number component.

param_16 float Default: 1100

The input value that is provided in the "Window Height" Number component.

param_17 str Default: "./tmp/record_videos"

The input value that is provided in the "Recording Path" Textbox component.

param_18 str Default: "./tmp/traces"

The input value that is provided in the "Trace Path" Textbox component.

param_19 str Default: "./tmp/agent_history"

The input value that is provided in the "Agent History Save Path" Textbox component.

param_20 str Default: "go to google.com and type 'OpenAI' click search and give me the first url"

The input value that is provided in the "Task Description" Textbox component.

Returns 1 element
str

The output value that appears in the "Status" Textbox component.

api_name: /lambda
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		provider="openai",
		api_key="",
		base_url="",
		api_name="/lambda"
)
print(result)
Accepts 3 parameters:
provider Literal['anthropic', 'openai', 'deepseek', 'google', 'ollama', 'azure_openai', 'mistral'] Default: "openai"

The input value that is provided in the "LLM Provider" Dropdown component.

api_key str Default: ""

The input value that is provided in the "API Key" Textbox component.

base_url str Default: ""

The input value that is provided in the "Base URL" Textbox component.

Returns 1 element
Literal['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o3-mini']

The output value that appears in the "Model Name" Dropdown component.

api_name: /lambda_1
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		enabled=True,
		api_name="/lambda_1"
)
print(result)
Accepts 1 parameter:
enabled bool Default: True

The input value that is provided in the "Enable Recording" Checkbox component.

Returns 1 element
str

The output value that appears in the "Recording Path" Textbox component.

api_name: /close_global_browser
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		api_name="/close_global_browser"
)
print(result)
Accepts 0 parameters:
Returns 1 element
api_name: /close_global_browser_1
copy
from gradio_client import Client

client = Client("http://localhost:7788/")
result = client.predict(
		api_name="/close_global_browser_1"
)
print(result)
Accepts 0 parameters:
Returns 1 element