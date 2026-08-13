from .utils import log_audit


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.method in ('POST', 'PATCH', 'DELETE'):
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) >= 2:
                model_name = path_parts[1]
                object_id = path_parts[2] if len(path_parts) > 2 else ''
                action_map = {'POST': 'create', 'PATCH': 'update', 'DELETE': 'delete'}
                action = action_map.get(request.method, 'update')
                log_audit(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    object_id=object_id,
                    description=f"{request.method} {request.path}",
                    request=request,
                )

        return response
