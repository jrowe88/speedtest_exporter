from twisted.web import resource
class IndexResource(resource.Resource):
    def render(self, request):
        page = "<!DOCTYPE html>" \
                "<html>" \
                "<head>" \
                "  <title>SpeedTest Exporter</title>" \
                "</head>" \
                "<body>" \
                "  <h1>SpeedTest Exporter</h1>" \
                "  <p><a href='metrics'>Metrics</a></p>" \
                "</body>" \
                "</html>"

        return page.encode('utf-8')
