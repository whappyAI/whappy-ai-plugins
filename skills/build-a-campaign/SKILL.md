---
name: build-a-campaign
description: Turn a business description or website into a rehearsed Whappy AI-setter campaign for WhatsApp or Instagram, then hand over to the Whappy dashboard to launch. Use when the user asks to create, set up or build a Whappy campaign, agent or AI setter.
---

# Build a Whappy campaign

Take the user from "here is my business" to a campaign that is built, checked and
rehearsed. Launching stays a click in the Whappy dashboard: this connector cannot
start a campaign, and you must never claim that it is live.

All tools below belong to the `whappy` MCP server. Your client may show them with a
prefix (for example `mcp__plugin_whappy_whappy__campaign_list` in Claude Code).

## 1. Understand the business

Ask for the website address, or a few sentences on what the business sells, to whom,
and what a qualified lead looks like (budget, timing, location, the appointment it
should book). Ask which channel the campaign should use: WhatsApp, Instagram or both.

## 2. Build it in one call

Call `agent_create_from_brief` once with the website and the description. It scrapes
the site, creates a new campaign with its funnel, knowledge documents and qualifying
questions, and runs the readiness check. It takes a minute or two: tell the user it is
working, and do not call it in a loop.

If the user wants to review each stage instead, use the staged tools:
`onboarding_generate_data_from_anything`, then `onboarding_generate_new_campaign`, and
`onboarding_get_status` to follow progress.

## 3. Review what was built

- Show the funnel with `funnel_get_by_campaign`. Change it only when the user asks,
  with `funnel_generate_from_instructions` or `funnel_process_map`.
- Show the knowledge with `context_list_by_campaign` and `context_get`. Edit with
  `context_create_or_update` or `context_update`.
- Show the qualifying questions with `info_list` and `info_get`. Edit with
  `info_create`, `info_update`, `info_add_example` and `info_remove_example`.
- Working hours, time zone and start delay: `settings_get`, then `settings_update`.
- Booking: `cal_get_settings` and `cal_event_types`, or `calendly_get_settings` and
  `calendly_event_types`, to check that the calendar the funnel books into exists.

Ask before any change, and never delete anything on your own initiative. Deleting a
campaign, a document, a question or a funnel step is the user's call, after you have
said what will be lost.

## 4. Connect the channel

- WhatsApp: `whatsapp_get_settings` lists the connected numbers. When none is
  connected, call `whatsapp_connect_link` and give the user the link: Meta's signup
  runs in their browser. Check again with `whatsapp_get_settings` afterwards.
- Instagram: `instagram_status`. When it is not connected, give the user the link
  from `instagram_connect_link`.
- WhatsApp on the user's own computer (Whappy desktop app): `desktop_status` says
  whether it is open to this account. Mention it only when the tool says it is.
- To change where the campaign talks, use `campaign_set_channels` with the full list
  of channels.

## 5. The first WhatsApp message

A campaign that writes first on WhatsApp needs a template approved by Meta.

1. `whatsapp_get_templates` lists the approved ones and why Meta rejected others.
2. If none fits, write one with `whatsapp_draft_template` and show the user the
   draft. Ask for a new draft to change it, and use `whatsapp_translate_template`
   for the same template in another language. `whatsapp_list_template_drafts` lists
   the saved drafts.
3. Only after the user says "submit", call `whatsapp_submit_template_draft`. Meta
   reviews it, which can take from minutes to a day.

## 6. Check and rehearse

1. `campaign_health` returns blockers, warnings and what is complete. Each blocker
   names the tool that fixes it. Fix the blockers with the user, then check again.
2. `campaign_rehearse` drives synthetic leads (cooperative, evasive, price only,
   confused, wrong language, impatient) through the funnel. They are test leads and
   are never messaged on WhatsApp. It returns at once and takes minutes: queue it once.
3. Poll `campaign_rehearsal_result`. While the status is PENDING or RUNNING there is
   no verdict yet: say so. When it is COMPLETED, report the pass rate and which
   persona got stuck on which question, and offer a fix. FAILED means the rehearsal
   could not run: it says nothing about the campaign.

## 7. Hand over to launch

Summarise: the campaign name, its channel, the health result, the rehearsal verdict,
and anything still pending (for example a template in Meta review). Then tell the user
to open the Whappy dashboard at <https://app.whappy.ai> and start the campaign there.

## Rules

- Never promise a result before a tool has returned it.
- Never invent a tool. If the user asks for something this connector cannot do (start
  a campaign, billing, account settings), point them to the dashboard.
- Keep phone numbers and message text of real leads out of your summaries unless the
  user asks for them.
