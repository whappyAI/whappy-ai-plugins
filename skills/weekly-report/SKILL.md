---
name: weekly-report
description: Produce a weekly Whappy report with leads, conversations, qualified leads and appointments, the funnel and where leads drop, plus the coaching suggestions waiting for a decision. Use when the user asks how Whappy did this week, for a weekly report, results, stats or analytics.
---

# Weekly Whappy report

Report the last seven full days (or the period the user names) for the whole account
and for each campaign that had activity. Read only.

All tools below belong to the `whappy` MCP server. Your client may show them with a
prefix (for example `mcp__plugin_whappy_whappy__stats_home` in Claude Code).

## 1. Fix the period

Use the seven days ending yesterday, as calendar dates in UTC (for example
`start_date=2026-11-15` and `end_date=2026-11-21`). Say which dates you used.

## 2. Collect

1. `campaign_list` for the campaign names and ids.
2. `stats_home` for the totals per campaign and for the whole account: leads,
   started conversations, closed conversations and appointments, with daily counts
   over the last 30 days. Sum the daily counts that fall in the period.
3. `analytics_overview` with `start_date` and `end_date`, once for the account and
   once per active campaign (pass `campaign_name` exactly as `campaign_list` shows it).
4. `analytics_funnel_visualization` with the same dates, for the stage counts and the
   overall conversion and error rates.
5. For each active campaign, `coach_campaign_report` (pass its `campaign_id`): the
   share of required information collected, completion rate, messages per
   conversation and the question missed most often.
6. `coach_list_proposals` for the suggested rewrites waiting for a decision.

When available, also use:

- `briefing_get` (when available) for Whappy's own weekly briefing, and
  `briefing_history` (when available) to compare with earlier weeks;
- `analytics_time_series` and `analytics_step_performance` (when available) for the
  trend and the step where leads drop;
- `analytics_by_channel` (when available) to split WhatsApp and Instagram.

Until they are available, compare with the previous week by running steps 3 and 4
again for the seven days before the period.

## 3. Report

1. **Headline**: three numbers for the period (new leads, qualified leads,
   appointments) with the change from the week before.
2. **Per campaign**: a small table with leads, conversations started, closed,
   appointments and conversion rate. Leave out campaigns with no activity and say how
   many you left out.
3. **Where leads drop**: the funnel stage with the biggest loss, and the question
   missed most often from the coach report.
4. **Suggestions**: each waiting proposal with its before and after text and the
   reason. Let the user choose; never apply one yourself.
5. **Next steps**: at most three, concrete. If a campaign looks broken (many errors,
   no conversations), run `campaign_health` and report its blockers.

## Rules

- Numbers come from the tools only. When a tool returns nothing, say "no data", not
  zero.
- Real leads only: the stats and analytics tools already leave out test leads.
- Keep lead names, phone numbers and message text out of the report.
