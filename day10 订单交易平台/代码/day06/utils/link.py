def filter_reverse(request, url):
    filter_string = request.GET.get("_filter")
    if not filter_string:
        return url
    return "/customer/list/?{}".format(filter_string)
