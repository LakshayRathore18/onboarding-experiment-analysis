# Onboarding Experiment: Answers

---

## Q1: Naive overall lift

| variant | n | conversion rate |
|---|---|---|
| control | 7,136 | 19.82% |
| treatment | 6,864 | 26.43% |

**Naive lift = +6.61 percentage points** (treatment − control).

That's the number leadership is excited about, and yeah, on the surface it looks like a clear win.

---

## Q2: Breakdown by segment

| segment | n_control | n_treatment | conv_control | conv_treatment | lift (pp) | z-score |
|---|---|---|---|---|---|---|
| app_store | 925 | 960 | 8.76% | 20.00% | **+11.24** | 7.07 |
| influencer | 119 | 131 | 23.53% | 16.79% | −6.74 | −1.33 |
| referral | 1,441 | 1,397 | 23.46% | 26.27% | +2.81 | 1.73 |
| paid_search | 3,353 | 1,459 | 15.18% | 14.39% | −0.79 | −0.71 |
| organic | 1,298 | 2,917 | 35.29% | 35.07% | −0.21 | −0.13 |

**Segment I would NOT trust: `influencer`.**

It shows the second-largest swing in the table (−6.74pp, a ~29% relative drop in conversion), which sounds alarming. But there are only 250 users in this segment total: 119 in control, 131 in treatment. The z-score is −1.33, nowhere near the ±1.96 you'd need for p<0.05. A swing this size with this few users is exactly what you'd expect from random noise; it could easily flip direction on a different sample. I wouldn't use it to argue the new flow hurts influencer users.

`app_store` also has a big lift (+11.24pp) but a z-score of 7.07, which is a completely different story. Covered under Q4.

---

## Q3: Mix-adjusted overall lift

For each segment I took its own (treatment − control) lift, then weighted it by that segment's share of the **total** population (not by how much of that segment happened to land in treatment):

| segment | share of total users | lift (pp) | contribution |
|---|---|---|---|
| paid_search | 34.37% | −0.79 | −0.271 |
| organic | 30.11% | −0.21 | −0.065 |
| app_store | 13.46% | +11.24 | +1.513 |
| referral | 20.27% | +2.81 | +0.570 |
| influencer | 1.79% | −6.74 | −0.120 |

Sum = **+1.63 percentage points**.

**Why is this so much lower than the +6.61pp from Q1?** The naive number implicitly weights each segment's lift by how many of that segment ended up in treatment, and the randomization was badly skewed (see Q5). `organic`, which has a 35% baseline conversion rate, was dumped 69% into treatment. `paid_search`, which converts at only 15%, went 70% into control. So the treatment group just happens to be packed with naturally high-converting users, and control is packed with naturally low-converting ones. Once you strip out that mix-shift and weight by actual population share, most of the gap disappears. It's a classic case of Simpson's Paradox: the aggregate looks great while almost every individual segment shows no improvement.

---

## Q4: Where is there a real effect?

**`app_store`.** Three things convinced me:

- The lift is huge: +11.24pp, more than doubling conversion from 8.8% to 20.0%.
- The z-score is 7.07. That's not a fluke. You'd have to be extraordinarily unlucky for that to be noise.
- The sample is well-balanced: 925 control, 960 treatment (49%/51%), so it's not an artifact of a skewed assignment like we see in organic and paid_search.

`referral` is directionally interesting too (+2.81pp, z = 1.73). The split is balanced and the direction is right, but z=1.73 gives a p-value around 0.08 two-tailed, so I'd call it "worth watching in the next experiment" rather than confirmed.

Every other segment (`organic`, `paid_search`, `influencer`) has a lift that's tiny or negative and nowhere near significant.

**The short version: rolling out the new flow to everyone is not justified by this data. It looks like it genuinely works for `app_store` users. For everyone else, the evidence ranges from weak to nothing.**

---

## Q5: Does assignment look off?

Yes, pretty clearly.

| segment | % control | % treatment |
|---|---|---|
| app_store | 49.1% | 50.9% |
| influencer | 47.6% | 52.4% |
| referral | 50.8% | 49.2% |
| **organic** | **30.8%** | **69.2%** |
| **paid_search** | **69.7%** | **30.3%** |

Three segments sit right around 50/50, which is what you'd expect from a proper per-user coin flip. But `organic` and `paid_search`, which together are 64% of all users, are both badly skewed in opposite directions. That's not bad luck; that's a broken randomization process. It looks like assignment happened at some level above the individual user, maybe by campaign, date, or channel, and that grouping happened to correlate with segment. This is exactly the confound that inflates Q1, and it makes me uneasy about even the near-zero lifts in organic and paid_search. I'd want to understand the root cause before feeling confident there aren't other hidden confounds inside those segments.

---

## Investigation process

- First thing I did was load the data and check for the obvious problems: nulls, weird values in `converted`, duplicate `user_id`s. All clean, 14,000 rows, no issues.
- Reproduced the naive topline number (+6.61pp) to confirm I'm starting from the same place as leadership.
- Broke conversion down by segment and immediately noticed baseline rates all over the place: 9% for app_store, 35% for organic. That screams confounding variable.
- Checked whether any user appeared in both variants (a classic A/B bug). They don't, `user_id` is unique throughout.
- Added z-scores to the segment breakdown to separate "looks big" from "is actually real." That's what separated influencer (big swing, pure noise) from app_store (big swing, rock solid).
- Briefly went down the path of treating influencer's negative lift as a possible backfire effect worth flagging in Q4. The n=250 and z=−1.33 killed that idea quickly. It belongs in Q2 as an example of what not to trust, not in Q4.
- Computed the mix-adjusted lift, double-checking that I was weighting by total population share (as the question specifies), not by treatment share. Verified the weights sum to exactly 1.0.
- Compared Q1 vs Q3 and looked at assignment ratios to figure out why they diverge so much. That's where the organic/paid_search skew jumped out.
- Wondered briefly if app_store's lift could be another assignment artifact, then checked: its split is 49/51, so that theory doesn't hold. The effect looks real.
- Manually summed weight × lift for each segment as a sanity check on the script's Q3 output. Both paths give 1.63pp.
