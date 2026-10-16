def errors_dict(form):
    """Flatten Django form errors to Inertia's ``{field: "message"}`` shape."""
    return {field: messages[0] for field, messages in form.errors.items()}
