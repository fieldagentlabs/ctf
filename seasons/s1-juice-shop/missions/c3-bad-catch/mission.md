# S1-C3 · Bad Catch

**Surface:** Claude chat · **Points:** 100 · **Time:** about 25 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

The morning after the breach, the shop's support inbox lights up. Customers are forwarding an email: their invoice "failed", and they need to "verify" their account. It looks like it came from the shop. It didn't.

The crew behind last night's break-in walked off with the customer list, and now they're fishing with it. Before the shop can warn customers and get the lookalike site taken down, the Directorate needs a clean list of indicators: where the email really came from, where it wants victims to go, and what it's carrying.

## Objectives

1. Download the email a customer forwarded: [`data/invoice_4471.eml`](data/invoice_4471.eml). If claude.ai won't accept `.eml` files, use [`data/invoice_4471.eml.txt`](data/invoice_4471.eml.txt): same email, text extension.
2. Upload it to [claude.ai](https://claude.ai) (any plan).
3. Have Claude parse the headers hop by hop and find where the email really originated.
4. Ask Claude for every indicator of compromise, with its type and how confident it is, as a **defanged** table you could paste into a ticket.
5. Submit the **lookalike sending domain** and the **originating IP**: `FA{DOMAIN_IP}`, for example `FA{bad.example_192.0.2.1}`. Defanged (`[.]`) is fine too.

Don't open the attachment in a browser. Ask Claude what it does instead.

## What you're practicing

- Uploading raw email to Claude and reading headers with it
- Building an IOC table you can hand to someone else
- Spotting the details that make a phish look real, and the ones that give it away

## Hints

- **Hint 1 (free):** The originating IP is the earliest external hop, read from the bottom.

## Field prep

[Claude 101](https://academy.claude.com/courses/claude-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
