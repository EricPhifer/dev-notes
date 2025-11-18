Put this HTML tag into the <head> of your website for near-instant navigation.
```
<script type="speculationrules">
  {
    "prerender": [{ "where": { "href_matches": "/*" }, "eagerness": "moderate" }],
    "prefetch": [{ "where": { "href_matches": "/*" }, "eagerness": "moderate" }]
  }
</script>
```
Ever clicked a link and had the next page appear almost instantly? That magical, speedy experience is becoming easier to achieve thanks to the Chrome Speculation Rules API. This new browser feature helps make navigation feel instant with just a few lines of HTML.
How does it work?
The Chrome Speculation Rules API allows developers to declaratively tell the browser which pages to preload and prerender, providing a near-instant loading experience:
"prefetch" tells the browser to only download the top-level HTML document for a linked page. It doesn’t render the page or fetch its sub-resources. This is less resource-intensive than prerendering but still saves time by having the HTML ready in the cache.
"prerender" instructs the browser to not only download a page but also to fully render it in background. This includes fetching all sub-resources like CSS, JavaScript, and images, and executing the JavaScript. When the user clicks the link, the page can be swapped into view almost instantly.
"eagerness": "moderate" is interpreted by browsers as: “Start the action 200ms after the user hovers their mouse pointer over a link.”
Press enter or click to view image in full size

Here’s a typical scenario:
A user is reading a page on your website.
They move their mouse cursor and let it rest over a link (e.g., “Services”).
The browser interprets this hover as a sign of intent. After a very brief delay (e.g., ~200 milliseconds, to avoid firing on accidental mouse-overs), it triggers the prerender or prefetch action for the “Services” page.
If the user then clicks the link, the page is already loaded (or at least partially loaded) in the background, resulting in a near-instant navigation.
Previously, for the docuseal.com website, we used Hotwired Turbo to achieve SPA-like navigation and to preload pages when hovering over links. Now, our website implements speculation rules, which allowed us to remove the Hotwired Turbo dependency and load heavy pages faster through prerendering.
Limitations
Speculation Rules API is supported only in Chrome 121 and later versions.
Press enter or click to view image in full size

For Firefox and Safari users, we created a short script to preload pages on hover so that they can be cached by the browser and reused once the hovered link is clicked. This also allows for near-instant navigation on browsers that do not support the Speculation Rules API. Heavy pages like the API might take a bit longer to load comparing to Chrome due to the lack of a pre-rendering mechanism natively supported by other browsers.
```
<script>
  if (!HTMLScriptElement.supports || !HTMLScriptElement.supports('speculationrules')) {
    const preloadedUrls = {};

    function pointerenterHandler () {
      if (!preloadedUrls[this.href]) {
        preloadedUrls[this.href] = true;

        const prefetcher = document.createElement('link');

        prefetcher.as = prefetcher.relList.supports('prefetch') ? 'document' : 'fetch';
        prefetcher.rel = prefetcher.relList.supports('prefetch') ? 'prefetch' : 'preload';
        prefetcher.href = this.href;

        document.head.appendChild(prefetcher);
      }
    }

    document.querySelectorAll('a[href^="/"]').forEach(item => {
      item.addEventListener('pointerenter', pointerenterHandler);
    });
  }
</script>
```
In order for this script to work on Firefox and Safari, pages should contain a Cache-Control header with a max-age value so that the preloaded page is cached on hover and then reused on link click.