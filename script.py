import os
import importlib
import pprint
import google.generativeai as genai

# Attempt to dynamically load an optional local helper to avoid static import errors
load_creds = None
try:
	mod = importlib.import_module("load_creds")
	load_creds = getattr(mod, "load_creds", None)
except Exception:
	load_creds = None

def _fallback_load_creds():
	api_key = os.environ.get("GOOGLE_API_KEY")
	if api_key:
		return {"api_key": api_key}
	return None

creds = None
if callable(load_creds):
	try:
		creds = load_creds()
	except Exception:
		creds = None

if not creds:
	creds = _fallback_load_creds()

if creds:
	# Try configuring the client with available credential shape
	try:
		genai.configure(credentials=creds)
	except Exception:
		try:
			genai.configure(api_key=creds.get("api_key"))
		except Exception:
			pass
else:
	print("Warning: no credentials found for genai. API calls may fail.")

print()
try:
	models = genai.list_models()
	print('Available base models:', [m.name for m in models])
except Exception as e:
	print('Error listing models:', e)