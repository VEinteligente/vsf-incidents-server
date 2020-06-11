class PageTitleMixin():
    """
    Passes page_title page_header, page_header_description, breadcrumb
    and active_tab into context, which makes it quite useful.

    """
    page_header = None
    page_header_description = None
    active_tab = None
    active_tab_class = None
    breadcrumb = None

    def get_context_data(self, **kwargs):
        ctx = super(PageTitleMixin, self).get_context_data(**kwargs)
        ctx.setdefault('active_tab', self.active_tab)
        ctx.setdefault('active_tab_class', self.active_tab_class)
        ctx.setdefault('page_header', self.page_header)
        ctx.setdefault('page_header_description', self.page_header_description)
        ctx.setdefault('breadcrumb', self.breadcrumb)

        return ctx
