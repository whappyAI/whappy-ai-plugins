---
name: daily-inbox-review
description: Summarise the Whappy inbox for today, listing unread chats, chats waiting on a human, chats in error and late desktop replies, and suggest what to do with each. Use when the user asks what needs attention in Whappy, for an inbox review, or for a morning check of their leads.
---

# Daily Whappy inbox review

Give the user a short, ordered list of the chats that need them today, and a
suggested action for each. Read only: this review changes nothing.

All tools below belong to the `whappy` MCP server. Your client may show them with a
prefix (for example `mcp__plugin_whappy_whappy__conversation_list` in Claude Code).

## 1. Collect

Run these reads. Use `page_size=20` and fetch more pages only while `has_next` is true
and the list is still useful (stop at 60 chats per group).

1. **Unread**: `conversation_list` with `is_unread=true` and `is_test=false`. These
   chats have a lead message that the AI has not handled and the owner has not opened.
2. **Waiting on a human**: `conversation_list` with `state="stopped"` and
   `is_test=false`. The AI is paused in these chats, so only a person can answer.
3. **In error**: `conversation_list` with `state="error"` and `is_test=false`.
4. **Late desktop replies**: only when `desktop_status` says WhatsApp desktop is open
   to this account, use `late_list` when available. Until then, say that late desktop
   replies are shown in the dashboard.

When available, `inbox_summary` gives the counts per campaign in one call. Use it for
the headline numbers and keep the lists above for the details.

To name the campaign of each chat, call `campaign_list` once and match on the
campaign id.

## 2. Look closer only where it helps

For at most five chats (the oldest unread and every chat waiting on a human), call
`conversation_get_by_lead` to read the last messages. It returns the whole history,
so read it for context and quote at most the lead's last message. Call `leads_get`
when you need the lead's name or campaign.

## 3. Report

Start with one line of counts, then one section per group, most urgent first:
waiting on a human, then unread, then errors, then late replies. For each chat give
the lead's first name, the campaign, how long ago the lead last wrote, and a one-line
summary.

## 4. Suggest actions

Suggest; do not act. For each chat, propose one of:

- **Answer it yourself** in the Whappy dashboard (<https://app.whappy.ai>), for chats
  where the AI is paused or the lead asked something only a person can answer.
- **Let the AI carry on**, by resuming the AI in the dashboard, when the pause is no
  longer needed.
- **Check the campaign**, when several chats of one campaign are in error: run
  `campaign_health` for that campaign and report its blockers.

The connector will later let the user act from here, each time only after the user
confirms that exact action. Use these only once the server lists them:

- `conversation_pause_ai` and `conversation_resume_ai`, when available;
- `conversation_reply`, when available: a reply only in a chat the lead opened, shown
  to the user as a preview first;
- `conversation_mark_read`, when available.

Never call a tool that the server does not list.

## Rules

- Real leads only: always pass `is_test=false` unless the user asks about test chats.
- Show phone numbers and full message text only when the user asks for them.
- If a list is empty, say so in one line; do not pad the report.
