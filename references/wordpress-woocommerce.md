# WordPress and WooCommerce Cloudflare Notes

## WordPress Safe Defaults

Good candidates for Cloudflare caching:
- Static assets under `/wp-content/uploads/`, themes, plugins, and fonts
- Public blog/category pages if using APO or well-tested full-page cache
- Public landing pages with no personalization

Bypass or be cautious:
- `/wp-admin/*`
- `/wp-login.php*`
- `preview=true`, customizer, editor routes
- `/wp-json/*` when authenticated, plugin-driven, or WooCommerce-related
- `admin-ajax.php` because many themes/plugins rely on it dynamically

## WooCommerce Hard Rules

Never cache personalized commerce flows:
- Cart
- Checkout
- My Account
- Order received/thank-you page when personalized
- Payment gateway callbacks/webhooks
- Add-to-cart query/action URLs
- Currency/location/session-based pricing pages unless engineered carefully

Common bypass patterns:
- `/cart*`
- `/checkout*`
- `/my-account*`
- `*add-to-cart=*`
- `*wc-ajax=*`
- Cookies containing `woocommerce_items_in_cart`, `woocommerce_cart_hash`, `wp_woocommerce_session_`, `wordpress_logged_in_`

## APO / Full Page Cache

Cloudflare APO can improve WordPress TTFB significantly for content sites. For WooCommerce:
- Use only with official plugin or validated cache bypass behavior
- Test logged-out, logged-in, cart, checkout, coupon, payment, and account flows
- Confirm `cf-cache-status` behavior differs for cacheable public pages vs cart/checkout

## Plugin Interaction

Avoid duplicate optimizations:
- If WP plugin minifies CSS/JS, Cloudflare Auto Minify may be redundant or risky.
- If image plugin serves WebP/AVIF, Cloudflare Polish may duplicate conversion.
- If plugin controls page cache, Cloudflare Cache Everything can conflict.

## WAF Caveats

Be careful with rules affecting:
- `/wp-json/` REST API
- `/wp-admin/admin-ajax.php`
- Payment gateway IPs/user agents
- Shipping/tax provider callbacks
- SEO crawlers and indexers
- Lark/Zapier/CRM/webhook integrations

For `/xmlrpc.php`:
- Block if not used.
- If Jetpack/mobile/pingbacks need it, challenge/rate-limit instead.

## Testing Checklist

After changes, test:
- Homepage anonymous
- Blog/article anonymous
- Login/logout
- Admin dashboard
- Add to cart
- Cart quantity update
- Checkout submit up to payment handoff
- Payment callback/sandbox if possible
- Coupon apply
- Search/filter/sort
- Mobile view
- Core Web Vitals or at least TTFB/LCP smoke test
