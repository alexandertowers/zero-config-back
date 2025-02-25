def hello_world(request):
    message = request.get_json().get("message", "Hello World")
    return f"Hello World: {message}"