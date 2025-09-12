# imports so I can get my API key from the .env file and set up OpenAI client
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("test.env")  # take my API key from the test.env file

client = OpenAI(api_key=os.getenv("API_KEY"))  # client is where you make API calls to
gpt_model = "o3-mini"
# gpt

response = client.responses.create(
    model=gpt_model,
    reasoning={"effort": "low"},
    input="Say 'hello world' in english and 2 other languages of your choosing"
)
'''
response = object returned by the API
client = the object that knows the API key and talks to the openAI servers
responses = response API endpoint 
.create = method to generate a new response from the gpt
client.responses.create() = send something to the model and generate an output

Other options that can be added to control the response:
- max_output_tokens, add structured inputs like text + strings or different roles within the input such as an english
responder + a spanish response
'''



###  print(dir(response))  # below is what was printed
# ['__abstractmethods__', '__annotations__', '__class__', '__class_getitem__', '__class_vars__', '__copy__',
# '__deepcopy__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__fields__', '__fields_set__',
# '__format__', '__ge__', '__get_pydantic_core_schema__', '__get_pydantic_json_schema__', '__getattr__', '__getattribute__',
# '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__',
# '__ne__', '__new__', '__pretty__', '__private_attributes__', '__pydantic_complete__', '__pydantic_computed_fields__',
# '__pydantic_core_schema__', '__pydantic_custom_init__', '__pydantic_decorators__', '__pydantic_extra__', '__pydantic_fields__',
# '__pydantic_fields_set__', '__pydantic_generic_metadata__', '__pydantic_init_subclass__', '__pydantic_parent_namespace__',
# '__pydantic_post_init__', '__pydantic_private__', '__pydantic_root_model__', '__pydantic_serializer__', '__pydantic_setattr_handlers__',
# '__pydantic_validator__', '__reduce__', '__reduce_ex__', '__replace__', '__repr__', '__repr_args__', '__repr_name__', '__repr_recursion__',
# '__repr_str__', '__rich_repr__', '__setattr__', '__setstate__', '__signature__', '__sizeof__', '__slots__', '__str__', '__subclasshook__',
# '__weakref__', '_abc_impl', '_calculate_keys', '_copy_and_set_values', '_get_value', '_iter', '_request_id', '_setattr_handler', 'background',
# 'construct', 'conversation', 'copy', 'created_at', 'dict', 'error', 'from_orm', 'id', 'incomplete_details', 'instructions', 'json', 'max_output_tokens',
# 'max_tool_calls', 'metadata', 'model', 'model_computed_fields', 'model_config', 'model_construct', 'model_copy', 'model_dump', 'model_dump_json', 'model_extra',
# 'model_fields', 'model_fields_set', 'model_json_schema', 'model_parametrized_name', 'model_post_init', 'model_rebuild', 'model_validate', 'model_validate_json',
# 'model_validate_strings', 'object', 'output', 'output_text', 'parallel_tool_calls', 'parse_file', 'parse_obj', 'parse_raw', 'previous_response_id', 'prompt',
# 'prompt_cache_key', 'reasoning', 'safety_identifier', 'schema', 'schema_json', 'service_tier', 'status', 'temperature', 'text', 'to_dict', 'to_json', 'tool_choice',
# 'tools', 'top_logprobs', 'top_p', 'truncation', 'update_forward_refs', 'usage', 'user', 'validate']

print(response.output_text)
