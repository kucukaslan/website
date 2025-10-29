---
title: "Frequently Asked Questions"
date: 2024-08-15T00:00:00+03:00
tags: [ 'personal', 'english' ]
draft: false
---

### Why is this website is so "plain"?

I don't see any reason for it not to be.
TBH, I do: a fancy website could've been more impressive for
talent hunters/recruiters also it would amaze my colleagues.

Personally I like [M. Çağrı Durgut](https://mcagridurgut.com/)'s website. It is fancy, displays his wit, its blog even
has dark mode. What more do people want?

Anyway.

Previously I used a Wordpress based website hosted on Digital Ocean or [webhosting](https://webhosting.com.tr) or
somewhere. But as it is obvious I don't actively maintain this website. So I don't need the extra features provided by
wordpress at the cost/burden of hosting a server.

I wanted to have my own domain, have a fancy name@surname.com.tr e-mail, to
turn [into Internet Landlord](https://landchad.net/#:~:text=into%20Internet%20Landlords) instead of being internet
peasant.

Moreover, I wanted to do this at minimal cost, at minimal effort.
This simple website is just a bunch of markdown files that are transformed to html files with Hugo. I host the content
on a GitHub Repository, updates to website are just `git push`es (or PRs) to master. A GitHub Action is triggered and
the update is deployed. Who is hosting it? Not me, thanks to [GitHub Pages](https://pages.github.com/). Not so
surprisingly, I have zero concern for uptime, zero concern for DDoS attacks, zero concern for vertical or horizontal or
diagonal scaling, zero concern for billing.

Similarly, I added SSL to my domain with [Cloudflare](https://cloudflare.com) for free. I don't have to worry about
renewing the certificate etc.

See also another similar website: [click here on you own risk](https://motherfuckingwebsite.com/)

### Why don't you have SSL (https) on your website?

I do have SSL if you type `https://` before [kucukaslan.com.tr](https://kucukaslan.com.tr). However, it is true that I
do not force redirects to `https`.

I will appeal to authority "Paul Graham" didn't either (at least for a long time).
See also [n-gate](http://n-gate.com/software/2017/07/12/0/) article.
