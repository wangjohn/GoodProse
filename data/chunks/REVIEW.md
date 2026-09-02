# Semantic chunk review

Every target is an exact contiguous span of the imported published post. Default chunks
begin as candidates; reviewed supplemental spans retain their checked-in status. A target
becomes an SFT example only after both its chunk and matching prompt are approved.

- Posts: 22
- Chunks: 114
- Splits: dev=19, test=20, train=75

## Cheap software won't make engineering cheap

### cheap-software-wont-make-engineering-cheap--001

`train` - `candidate` - 159 approximate tokens - 120 words

Headings: (intro or continuation)

```markdown
In a world where AI writes more and more of the code, is it crazy to still want to be a software engineer? My answer is no. I think there will still be a reasonably large number of engineers in the future, and some of them will be incredibly well paid.

I'm not necessarily saying there will be more of them than there are today. But if you're an engineer (or whatever the future version of the job ends up being called) and you know how to build high-quality systems that solve real needs, you're going to be very valuable.

Two things seem likely to me, and both are already visible if you look at how other industries have evolved.
```

### cheap-software-wont-make-engineering-cheap--002

`train` - `candidate` - 690 approximate tokens - 466 words

Headings: Software will follow Jevons paradox

```markdown
# Software will follow Jevons paradox

Jevons paradox is the observation that as something gets more efficient, we tend to use more of it, not less. [William Stanley Jevons noticed](https://en.wikipedia.org/wiki/Jevons_paradox) that when James Watt dramatically improved the steam engine, factories ended up burning more coal, not less. Cheaper power meant factories could produce more, businesses expanded their operations, and total coal consumption went up.

It's very likely that coding is going to get a lot cheaper. That means we'll likely end up with far more software than exists today as it becomes cheaper and more possible to build. For example, every family might end up with its own custom app for running the household, or you might see every company customize their internal tools way more. Will professional software engineers be needed for all of this software? Probably not all of it, especially as it becomes easier and easier to write and maintain. But generally when markets expand, the need to have someone managing at least some of that software becomes pretty high.

The other thing that I've noticed is that as things gets more efficient, the distribution of the thing tends to get broader and luxury goods tend to appear. More efficiency means more choice, and people sort themselves across the premium and the economy ends of the market.

- **Fashion.** Most people can now afford a closet full of shirts and shoes. In the 1800s you used to only own a few pieces of clothing, but now manufacturing scale has made pretty much all clothes incredibly cheap. That has allowed the development of ultra-high end clothing: <span class="no-math">handmade suits, \$200+ merino wool t-shirts, \$5k+ jackets, etc.</span>
- **Air travel.** Similarly, as planes got more efficient over the decades, the cost of a ticket dropped precipitously and more people fly than ever before. But at the same time, the distribution of what it looks like to fly is wider than ever before. We now have basic economy seats where you can't bring a carry on. But you also have first class suites and private jets. There's much more dispersion than ever before.

I think software engineering will play out the same way. You'll have a lot more software than there used to be, and you'll also have a high end that is far higher end than it ever was. The handful of people who still know how to build hardened production software, systems that scale to massive levels of compute, stay reliable, and get the tradeoffs right, will be even more in demand than they are today. The middle falls away and you get a bimodal distribution, much like air travel: either you're paying tens of thousands of dollars for the first-class or private experience, or you're in economy.
```

### cheap-software-wont-make-engineering-cheap--003

`train` - `candidate` - 619 approximate tokens - 390 words

Headings: Engineers will orchestrate more

```markdown
# Engineers will orchestrate more

The other shift is in actual job that will be done by engineers. I recently read [what pilots actually do on a 14-hour flight](https://simpleflying.com/what-pilots-actually-do-14-hour-flight-autopilot-handleing-everything/), which is a fascinating corollary to what I think will happen in software.

In commercial flights, the autopilot handles the flying of the plane on basically the entire flight, and the pilots physically fly the plane for only takeoff and landing. But the pilots' main jobs have shifted to handling communication with air traffic control, managing flights paths to look out for weather and turbulence, and handling contingency planning to develop a safe backup plan for each scenario. Arguably this is something that pilots could do before, but they're likely much better now that it's their main focus. Notice too that the job has switched from a in-the-zone, focused task of flying the plane to something that is much more interrupt and monitoring based.

This is roughly what I expect for software engineers as the act of writing code keeps getting automated.

There are a lot of articles making this case, but the general thesis is that engineers will spend their time on everything in the stack other than the pure implementation: the product requirements, the design, overseeing the implementation, making sure there's enough testing, the rollout, the maintenance, talking to customers.

We've seen this type of morphing happen before. In [an interview with Cursor's co-founder](https://www.youtube.com/watch?v=bWyOyyrVIXk), Simon Eskildsen (creator of Turbopuffer and Logrus, and a deeply skilled infrastructure engineer) describes how in the early 2010s you started to see DevOps engineers emerge: people who could both SSH onto a machine and write configuration. Before that, ops was its own role, people who managed the servers but didn't write code. Over time that blended into what we now call production engineering: people who can code but also have deep expertise in Kubernetes, Terraform, AWS/GCP, observability, and logging. Now you don't need as many people handling your devops, but the people who you still do need are way more valuable.

I think the generalist engineer is about to go through a similar morph, just pointed in a different direction of some hybrid of engineer, product manager, and designer. The deep implementation skill hopefully won't disappear, but it stops being the whole job.
```

### cheap-software-wont-make-engineering-cheap--004

`train` - `candidate` - 366 approximate tokens - 252 words

Headings: So will the future be good?

```markdown
# So will the future be good?

I think there will be some ways in which the future is nicer, and other ways that will be extremely unfun.

The future will be great because access to really custom software will likely get democratized. It's going to be easy to have software that conforms much more exactly to what you specifically are looking for, and you'll be able to build a lot of it yourself. The quality of life should keep climbing now that software can become more specifically built for you. I'm excited for things like access to better health information and much more customized health diagnoses that accessible much more readily. I'm also excited for much easier ability to talk across different languages as compute and translation become easier to put into devices.

At the same time, the future might not be as fun because I think we'll keep seeing stratification and a steadily rising Gini coefficient. The goods that are rival and zero-sum (housing in the places people want to live, access to really high quality education, etc.) derive their value from scarcity, so they don't get cheaper as everything else does. They tend to do the opposite usually as a few people accumulate more wealth, which seems very likely in a world with more, cheaper software.

So, the future will see a lot of change. I think the base layer of life will keep getting better and more customizable, while the scarce, positional stuff will keep getting harder to reach.
```

### cheap-software-wont-make-engineering-cheap--sentence-001

`train` - `approved` - 49 approximate tokens - 35 words

Headings: (intro or continuation)

```markdown
But if you're an engineer (or whatever the future version of the job ends up being called) and you know how to build high-quality systems that solve real needs, you're going to be very valuable.
```

## How we learned to stop worrying and love the AI in coding interviews

### external-ai-coding-interviews--001

`dev` - `candidate` - 271 approximate tokens - 159 words

Headings: (intro or continuation)

```markdown
I remember my 5th grade math teacher told me I needed to memorize square roots because “you won't always have a calculator with you".

Technology changes quickly, and banning AI from technical interviews in 2025 feels eerily similar to banning calculators from math tests in the 90s. Ironically, many well known AI companies are still preventing candidates from using AI in technical assessments (see [Anthropic](https://www.ft.com/content/9b1e6af4-94f2-41c6-bb91-96a74b9b2da1) for example).

At Assembled, we actively encourage AI tools in certain technical interviews. Candidates have really enjoyed these interviews as they offer an authentic preview of our work environment. It also provides us with much clearer signals about a candidate’s day-to-day engineering work.

To be clear, we haven't abandoned traditional interviews entirely — we still have dedicated sessions focusing on core CS fundamentals without AI assistance. But we believe a balanced engineer needs both skills: the ability to understand concepts deeply _and_ the ability to leverage modern tools effectively.
```

### external-ai-coding-interviews--002

`dev` - `candidate` - 356 approximate tokens - 224 words

Headings: The reality of modern engineering / New types of interviews

```markdown
## The reality of modern engineering

Our engineers don't write most of their code from scratch anymore. We use Cursor, Claude Code, GitHub Copilot, and other AI tools for a significant portion of our day-to-day coding. This isn't a dirty secret, it's just how modern engineering works.

I’ve personally seen my productivity skyrocket since incorporating these tools. They’ve sped up everything from mundane tasks like writing tests to more complex but boilerplate-y work, like distributing WebSocket connections across servers.

A few years ago, we evaluated candidates on their ability to search Google or use an IDE effectively. We’ve now done the same with today’s generation of tools, which just so happen to be largely powered by AI.

## New types of interviews

Many of our past questions that prioritized coding fundamentals can be one-shotted with AI (which makes for a pretty boring interview experience). When we first introduced AI into our interviews, a candidate used ChatGPT to solve our standard algorithm challenge in under three minutes, leaving us with 40 minutes of awkward small talk.

We’ve redesigned our interviews to better reflect the qualities we care about. Instead of FizzBuzz-type challenges, we now ask candidates to solve a scoped problem end to end, by building the backend and frontend. These problems have open ended design requirements—there's no right or wrong answer to most of them.
```

### external-ai-coding-interviews--003

`dev` - `candidate` - 621 approximate tokens - 365 words

Headings: Finding great engineers

```markdown
## Finding great engineers

When you join Assembled’s engineering team, we don’t really care if you can implement Quicksort from memory or if you can balance a red-black tree without documentation: we care about whether you can write maintainable, well-tested code that solves real user problems.

After running dozens of AI-assisted interviews, we've identified a few patterns that distinguish exceptional engineers. The strongest candidates:

*   **Have used AI tools extensively to write better, faster code**. One candidate impressed us by using AI to set up a complex data structure, but then customized the critical sections with their own optimizations. Another used AI to summarize unfamiliar API documentation, allowing them to focus on the architecture decisions in the interview.
*   **Actually understand the problem before building**. This sounds obvious, but you'd be shocked how many people jump to implementation without understanding what needs to be done. A recent standout candidate asked a handful of piercingly thoughtful questions about use cases and then quickly incorporated that nuanced understanding into the end product.
*   **Apply critical judgment to code, regardless of source.** Strong engineers don't blindly trust AI output but rather methodically evaluate, debug, and verify the generated solutions. One impressive candidate identified subtle bugs in an AI-generated algorithm that even our interviewers initially missed.
*   **Make good product decisions.** The best candidates aren’t satisfied with code that merely meets the criteria, they’re generally thinking about what elevates the experience: from engineering specific things like performance, fault tolerance, and scalability to more general usability concerns like how a user will interact with their design. As AI handles more of the implementation details, engineers will make more product decisions than ever before. Having good "taste", i.e. knowing where to invest your effort for maximum impact and which details matter for user experience, is a crucial skill we're evaluating.

On the other end of the spectrum, weaker candidates reveal consistent patterns that limit their effectiveness with AI tools. They often treat AI as a magic solution generator by feeding in prompts and accepting whatever comes back without much scrutiny. We’ve also seen candidates lack the technical judgment to evaluate AI-generated solutions or get stuck on bugs that AI couldn’t solve out of the box.
```

### external-ai-coding-interviews--004

`dev` - `candidate` - 299 approximate tokens - 177 words

Headings: Raising the bar

```markdown
## Raising the bar

We've significantly increased our expectations for what candidates should accomplish during the interviews that allow AI. Where we once might have been satisfied with a basic backend implementation, we now expect candidates to build a relatively complete frontend, backend, and make significant progress on edge cases and optimizations within the same time frame.

Understanding computer science fundamentals remains important, but the emphasis has shifted from "can you implement this from scratch" to "can you guide AI and then recognize whether an implementation is correct and efficient." This mirrors the reality of modern engineering, where prompting and evaluating code often outweighs writing it from scratch.

At Assembled, we believe technical interviews should evaluate how candidates will perform in the actual job — not in an artificial environment with arbitrary constraints. Our engineers use AI tools in their daily work, and our interview process reflects that reality.

_If you're interested in a technical role at Assembled where we're building AI systems to transform customer support, check out our_[_open positions_](https://www.assembled.com/careers)_._
```

## Better RAG results with Reciprocal Rank Fusion and Hybrid Search

### external-better-rag--001

`train` - `candidate` - 374 approximate tokens - 209 words

Headings: The problem with vector-only search

```markdown
## The problem with vector-only search

At Assembled, [our issue resolution engine](https://www.assembled.com/features/assembled-assist) is designed to assist customer support by suggesting potential answers to support queries. We use Retrieval Augmented Generation (RAG) for much of this pipeline because it's quicker to iterate on than fine-tuning, doesn’t require training on customer data (which many companies prefer), and generally provides high-quality results.

However, we encountered a significant challenge with RAG: relying solely on vector search (even using both dense and sparse vectors) doesn’t always deliver satisfactory results for certain queries. This issue was particularly evident when users entered specific keywords that didn’t accurately match stored knowledge articles.

Customer support teams often have multiple articles on similar topics and lack a tightly curated knowledge base, leading vector search to sometimes return irrelevant results to our RAG engine and reduce response accuracy. Users familiar with traditional keyword searches were puzzled when our system couldn't find the right documents, especially for short queries with prominent but ambiguous keywords.

For example, if a user asked “what features are included in a premium plan?”, vector search would excel at pulling documents about different plans, customer testimonials, or marketing materials. However, vector search would often fail at finding articles specifically targeting premium plans.
```

### external-better-rag--002

`train` - `candidate` - 510 approximate tokens - 309 words

Headings: The solution: Hybrid Search with Reciprocal Rank Fusion / Document store abstraction

```markdown
## The solution: Hybrid Search with Reciprocal Rank Fusion

To address this issue, we integrated a new keyword search infrastructure that combines its results with vector search for optimal performance. In the above example, keyword search would hone in on “features”, “premium”, and “plan”, and narrow search results to documents specifically matching these keywords. A hybrid approach with both vector and keyword search allows us to effectively return articles with semantic matches while also providing users with the familiar feel of traditional keyword search. Our intuition was based on our experience with other machine learning systems where ensemble models generally outperform single models.

### Document store abstraction

To enable a hybrid store solution, we developed a document store abstraction in our code, allowing us to integrate multiple search algorithms. The abstraction is simple but captures all the essential functionalities of a document store and search system. It handles document management and querying and is agnostic to the actual implementation (vector search, keyword search, etc.). Here’s what it looks like:

With this abstraction, we had the primitives we needed to swap different search systems in and out easily. Uploading a document could be done once and then sync across multiple document stores. Similarly, searching for a document could be done in parallel across multiple document stores using a standardized query.

The interesting part is that our hybrid search store itself implements the **`DocumentStore`** interface. This means that, from the perspective of the caller, it doesn't matter whether they are interacting with a single store or our complex hybrid store — they use the same interface and methods. This design ensures that all of the logic for determining which documents are retrieved is hidden from the caller and can be tested separately. To implement the hybrid store, we passed in multiple child document stores and parallelized the search across all of the child stores.
```

### external-better-rag--003

`train` - `candidate` - 362 approximate tokens - 210 words

Headings: Syncing documents across stores

```markdown
### Syncing documents across stores

Enabling multiple document stores introduced technical challenges, especially around ensuring synchronization. Out-of-sync document stores could lead to subtle bugs, such as a document being present in one store but not another. To address this, we implemented the following:

*   **Single source of truth:** We maintain a document store in PostgreSQL (for metadata)and S3 (for the actual documents themselves) as a source of truth. This store implements document storage interfaces but is not included in queries. It serves solely for record keeping, allowing us to resync content if necessary.
*   **Asynchronous updates:** Due to higher latency in storing articles, we first update our source of truth in the database and provide an acknowledgement to the frontend. We then asynchronously store the documents in our child stores. This approach helps manage latency across multiple stores and ensures our document stores are eventually consistent.
*   **Error handling:** We also need to handle errors across different platforms. For example, one store might experience a network outage while another completes the storage process successfully. Our PostgreSQL database tracks the synchronization status of each store. If a store fails to sync, we employ [exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff) to retry the operation, ensuring that all stores are eventually brought into sync.
```

### external-better-rag--004

`train` - `candidate` - 512 approximate tokens - 295 words

Headings: Combining results across multiple search engines / Weighting-based fusion / Rank fusion

```markdown
## Combining results across multiple search engines

To optimize search performance, we explored several algorithms for merging the results from our different document stores.

### Weighting-based fusion

Our initial approach involved experimenting with various weighting mechanisms for sparse/dense vectors and keyword search. The goal was to find optimal weightings that leverage the strengths of each search method. However, identifying the correct weightings proved challenging due to the unknown distribution of vector search scores. This variability made it difficult to determine the relative importance of different weightings.

What’s more, empirical data showed that similarity scores (dot product and Euclidean distance) varied widely across our customer base. The differential performance across these metrics made it impractical to develop a universal weighting scheme for combining vector and keyword searches. Tuning these weights on a per-customer basis was not scalable.

### Rank fusion

Next, we turned to rank fusion algorithms, inspired by literature reviews and their demonstrated effectiveness in search optimization (see [[0]](https://rodgerbenham.github.io/bc17-adcs.pdf) and [[1]](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)). Rank fusion algorithms, particularly Reciprocal Rank Fusion (RRF), provided a promising alternative. Here’s how most rank fusion algorithms work:

1.   **Rank assignment:** Each document from the individual ranked lists is assigned a score based on its rank position. Typically, the score is the reciprocal of its rank (i.e., 1/rank). For example, a document ranked first gets a score of 1, the second gets 0.5, the third gets 0.33, and so on.
2.   **Score summation:** The scores from all ranked lists are summed for each document. Documents appearing in multiple lists accumulate higher combined scores.
3.   **Final ranking:** Documents are re-ranked based on their combined scores, producing a final ranked list that integrates the rankings from all individual search engines.
```

### external-better-rag--005

`train` - `candidate` - 602 approximate tokens - 326 words

Headings: Why we chose RRF / Optimizing our search infrastructure

```markdown
### Why we chose RRF

After extensive testing, Reciprocal Rank Fusion (RRF) consistently outperformed many of the more complex methods we evaluated. Several factors contributed to this:

*   **Simplicity and robustness:** RRF's simplicity makes it less prone to overfitting specific scenarios, aligning with the principle of [Occam’s razor](https://en.wikipedia.org/wiki/Occam's_razor). This simplicity enhances its robustness across different contexts.
*   **Minimal tuning:** RRF provides a straightforward and effective way to rank results without the need for extensive parameter tuning. This is particularly advantageous given our diverse customer base and their varying knowledge bases.

By implementing RRF, we achieved a flexible and scalable method for combining search results. Using RRF, we not only enhanced the accuracy and relevance of search outcomes but also simplified the overall search infrastructure, ensuring a robust solution for our diverse customer set.

## Optimizing our search infrastructure

Finally, a note on our search engine choices. At Assembled, we use [Pinecone](https://www.pinecone.io/) for vector search and [Algolia](https://www.algolia.com/) for keyword search. After minimal testing with other providers, we concluded that the marginal benefits of further optimization were not significant. Consequently, we decided against hosting our own open-source vector database, such as [Milvus](https://github.com/milvus-io/milvus), or managing our own keyword search on [Elasticsearch](https://github.com/elastic/elasticsearch).

Using B2B solutions like [Pinecone](https://www.pinecone.io/customers/assembled/) and Algolia offers several advantages:

*   **Cost efficiency:** These services are reasonably cost-effective (especially when comparing to engineering time) and eliminate the need for significant upfront investment in infrastructure.
*   **Maintenance reduction:** Like most companies, we’re resource constrained by engineering resources, so by outsourcing to specialized search companies, we avoid the substantial maintenance burden associated with self-hosted solutions. This allows our team to focus on our core functionality of AI replies for support issues.
*   **Performance:** Algolia in particular provides low-latency responses, a robust API, and highly optimized search outputs which would likely outperform anything we could build on Elasticsearch.
```

### external-better-rag--sentence-001

`train` - `approved` - 31 approximate tokens - 17 words

Headings: (intro or continuation)

```markdown
To optimize search performance, we explored several algorithms for merging the results from our different document stores.
```

## Why blocking LLMs from your website is dumb

### external-blocking-llms--001

`train` - `candidate` - 400 approximate tokens - 257 words

Headings: (intro or continuation)

```markdown
Perplexity was recently accused of [scraping sites that had explicitly disallowed LLM crawlers](https://techcrunch.com/2025/08/04/perplexity-accused-of-scraping-websites-that-explicitly-blocked-ai-scraping/) in their robots.txt files. In the wake of that revelation, a wave of how-to guides for blocking large-language-model scraping has surfaced [0]. They’re generally highly vitriolic, with people opposing this on both moral grounds (“AI is stealing your content”) as well as displaying a general distaste for AI.

**But how many of you wouldn’t hook up your website to Google?**

I know one of the primary reasons that I do anything online is to provide an outlet for someone else to see it. If I didn’t want someone else to see it, I’d write it down on my notebook, not on the public web.

LLMs are the next generation’s search layer. They’re already generating massive amounts of pipeline for the companies and websites that have gotten good at getting their content displayed in LLMs. Combine that with the fact that most LLMs have an agentic web-search component that will actively generate links, and you have a massive funnel of potential readers for your content.

Blocking that pipeline may feel righteous, but it also cuts you off from the fastest-growing distribution channel on the web.

Just like any technology, using LLMs correctly harnesses a ton of power, and completely trying to block the technology is generally a bad idea. I think the upside goes to creators who adapt, not those who hide.

Providing high quality content that LLMs will actually cite is the new game in town.
```

## Code review bottlenecks: how we hill climbed our way to higher PR throughput

### external-code-review-bottlenecks--001

`train` - `candidate` - 291 approximate tokens - 198 words

Headings: (intro or continuation)

```markdown
After we adopted coding agents at Assembled, engineers kept telling me they felt much faster. But when we looked at our delivery metrics, the improvement was much smaller than we expected. We were writing more code and creating more PRs, but only merging slightly more of them. Time to first review had increased from a median of 3.5h to over 16h, and it was becoming normal to see an engineer with dozens of PRs waiting in a single Graphite stack.

We dug into our engineering productivity data and found that human code review had become the bottleneck. So we built an automated reviewer that approves low-risk PRs. The early results are very promising and showed PRs merged reaching **2.4× of our pre-agent baseline**. Most surprisingly, throughput for large PRs increased **3.5×**, even though the auto-reviewer generally did not approve them. Much of the new throughput is centered on bugfixes (3.7x above baseline) and refactors (7.5x above baseline), but we also saw accelerated feature development (2.5x above baseline).

This post covers how we found the bottleneck, how we built the auto-reviewer, and our hypotheses for why it worked as well as it did.
```

### external-code-review-bottlenecks--002

`train` - `candidate` - 434 approximate tokens - 285 words

Headings: Reviewers couldn't keep up with agent-generated code

```markdown
## Reviewers couldn't keep up with agent-generated code

For some context, we sell customer support software to companies like Salesforce and DoorDash, as well as organizations like the State of Georgia. Hundreds of thousands of support agents rely on our product being stable. Vibe coding without verifying correctness was never an option for us. Still, we felt like we should be moving faster given the coding agents and other AI tools we now had access to.

So we did an investigation into our engineering productivity. As we dug into the metrics, we found a few things:

*   **The number of open PRs was much larger than before**, and the majority of them weren't getting merged (and if they were, they weren’t getting merged quickly).
*   **Stacks were getting deeper.** Engineers were breaking big features into reviewable pieces, which is the right instinct, but it regularly produced stacks of 20 PRs for a single project.
*   **Time to first review was up** from a median of 3.5h in December 2025 to over 16h in May 2026, driven by a much larger incoming PR count.
*   **PR size had increased 2.5x**, since agent-written diffs tend to be larger than the human-written version of the same change.

There were also costs that didn't show up on a dashboard. Engineers had to multiplex across several agent jobs to stay effective, which meant people who were used to concentrating on one thing were now juggling several. More non-engineers were writing PRs (which we wanted), but those PRs didn't always follow established engineering conventions, so reviewing them carried emotional burden.

Every property of coding agents points toward more code, but we were still routing all of it through the same number of human reviewers.
```

### external-code-review-bottlenecks--003

`train` - `candidate` - 431 approximate tokens - 261 words

Headings: Setting up an automated reviewer for low-risk PRs

```markdown
## Setting up an automated reviewer for low-risk PRs

To alleviate this, we started with the safest possible experiment: auto-approving test-only PRs. It worked fine, but there were relatively few test-only PRs (only a handful per week), so it didn't move the needle perceptibly.

Then we got more aggressive and built a review system directly into [143.dev](http://143.dev/), our internal coding agent platform [0]. The system:

*   **Runs two independent reviews.** Codex (GPT-5.6-sol, high) and Claude Code (Claude Opus 5, high) each review the PR in separate cloud sandboxes. We intentionally made the prompts simple, using the built-in `/review` command. OpenAI and Anthropic have enormous resources making sure their agents work well for review, so we leveraged that as much as possible.
*   **Makes an approval decision.** An orchestrator agent (GPT-5.6-sol, high) pulls in both reviews, applies our approval policy, and decides whether the PR gets auto-approved. The approval policy includes both deterministic rules (e.g. only approve PRs under 1000 lines changed) as well as LLM-based policies (e.g. don’t approve any changes in credential or secret handling or cryptographic key management).

We spent a large amount of time tuning the policy that we use, landing on something similar to the following:

*   A good PR description
*   High-quality testing evidence: screenshots or videos for product changes, or direct evidence that the change does what it claims
*   An implementation that follows established repository patterns
*   No changes to risky areas like authentication, billing, or permissions
*   No new architectural patterns
*   A few other guardrails based on failure modes we saw during rollout
```

### external-code-review-bottlenecks--004

`train` - `candidate` - 289 approximate tokens - 196 words

Headings: Iterating on the policy

```markdown
## Iterating on the policy

As Greg Mankiw says: “People respond to incentives” and the auto-approval policy was the ultimate version of this. We saw that our engineers ended up shaping PRs for the approval policy, so whatever the policy rewards, you get more of.

This meant we had to be very thoughtful about what we wanted to let through. We realized that the only usable version of an auto-approval policy was one with high integrity and broad coverage. When there was low coverage (e.g. it doesn’t auto-approve enough things), the reviewer didn’t get enough traction to be used and people abandoned or forgot about it.

At the same time, we needed to ensure we weren’t approving low quality PRs either:

*   Policy too loose: people route work through it precisely because it doesn't look closely, mistakes compound in master, and we have an incredibly dangerous buildup of bugs.
*   Policy too strict: it fails silently and you never recover usage. Engineers try it twice, get rejected, and stop asking, which means you save no review time and stop learning where the policy is wrong.

So the job was to hold a narrow ridge between the two cliffs.
```

### external-code-review-bottlenecks--005

`train` - `candidate` - 538 approximate tokens - 345 words

Headings: Rolling out safely

```markdown
## Rolling out safely

We found the best way to make adjustments to the policy to tune it towards the “Useful automation” region was a phased approach:

*   **Start with trusted alpha testers and review everything.** We launched with a small group that reported both false positives and false negatives, with much more scrutiny on false positives. Before a wider launch, a mistaken approval would still be noticed by the group. The team that owned the policy also reviewed **every PR** as they came in and compared its decision with the system’s. Surprisingly, we found that our initial policy was far too conservative. We had added a lot of restrictions that were not buying us meaningful safety, and the reviewer rejected so much that engineers were unlikely to keep using it.
*   **Expand gradually, with audits and direct feedback.** Once we were confident in the initial behavior, we rolled it out more broadly.
    *   We started with daily reviews of approval quality, then moved to a regular cadence as usage and confidence grew. We also built automations that scanned review sessions and identified recurring failure patterns.
    *   Engineers could request a re-review or leave free-form feedback directly on the PR. The 143 reviewer categorized that feedback for the admins, who could then decide whether the policy needed to change.

*   **Track usage and approval rates by engineer.** We added a dedicated page in 143 showing who was requesting the most auto-reviews and what percentage of their PRs were being approved.
    *   This was unusually useful because aggregate approval rates hid very different behaviors. We could talk to power users to understand how they were using the system (and whether they were finding ways to game it). We could also talk to infrequent users to understand what was keeping them away.

The goal was to begin with a narrow set of changes where we could establish trust, then gradually expand coverage as our evidence and guardrails improved. The policy needed to be strict enough that an approval meant something, but useful enough that engineers would actually change their behavior to qualify for it.
```

### external-code-review-bottlenecks--006

`train` - `candidate` - 682 approximate tokens - 454 words

Headings: Results: 2.4× more PRs merged

```markdown
## Results: 2.4× more PRs merged

The metrics from our rollout were incredible and they far exceeded our initial expectations:

*   **PRs merged rose to 2.4× of our pre-agent baseline.** Lines of code rose by 2.8×, so we weren't just slicing the same work into more PRs.
*   **Auto-approvals grew to 43% of merges** over the three weeks after the full-team launch.
*   **Large PRs (600+ lines) increased 3.5× in throughput**, with p90 wait time holding steady.
*   **Refactoring went up 7.5× and test work went up 3.4×.** Nearly half of our peak week was debt paydown we'd previously never gotten to.
*   **Bugs reported per week went down 27%** and **reverts per PR stayed steady at 0.8%**. Note this window is too short to be conclusive, especially because of the time delay of bugs being reported, but it is encouraging and these are numbers we’ll continue to check.
*   **Non-engineers accounted for 13% of all PRs.** We had a stricter approval policy set up for designers, PM, and customer support, but we still allowed auto approval for small changes (updating copy, fixing bugs, etc.). The auto-reviewer, combined with cloud agents like Devin, allowed non-engineers to contribute significantly without requiring a large amount of engineering handholding.

These are observational results from a rollout, not a randomized trial, and we don't think the auto-reviewer gets credit for every point of movement (and there are still observations of bugs and long-term quality that need to be made). But the timing, the composition of the extra work, and what engineers told us point to a few mechanisms at work:

**Fast, predictable review changed which work people attempted.** The median auto-review takes eight minutes, and just as importantly, you know roughly when it's coming and what bar you have to clear. Before, an engineer who noticed a minor refactor or a missing test had to decide whether it was worth consuming a human reviewer's attention. These PRs were easy to deprioritize because they weren’t urgent. With a reliable fast lane, engineers became much more willing to spin off small improvements. If you're in an area of the codebase and see something small worth fixing, it's now easy to kick off a separate job and get it reviewed quickly. This is a big part of why refactoring grew 7.5x while overall output grew 2.4x.

**Much of the new speed centered on bug-fixes and performance work.** Instead of unleashing a bevy of bad PRs, the auto-reviewer has actually encouraged better code because of the ease at which smaller bugfixes and targeted performance work move through the system. We’ve seen our primary database CPU usage decrease by 20% as teams set up automations to improve slow queries they owned.
```

### external-code-review-bottlenecks--007

`train` - `candidate` - 280 approximate tokens - 183 words

Headings: (intro or continuation)

```markdown
**The policy improved the PRs themselves.** To qualify for auto-approval, a PR needs a real description, direct testing evidence, and an implementation that follows existing patterns. Engineers adapted to this quickly. More PRs showed up with testing evidence at the top and screenshots of the change, and large changes got broken into smaller units so each piece was more likely to qualify. This raised the baseline quality of all PRs, including the ones humans review, and it pushed the codebase toward smaller, cleaner changes, which is something we wanted anyway.

**Removing small PRs from the queue helped the large ones.** This was the most counterintuitive result, since large PRs sat outside the fast lane of auto-approvals. Our best explanation is that review capacity is about concentration as much as hours. Reviewers were no longer being bombarded by small, conventional PRs all day, so when a PR did land in their queue, they knew it actually needed their attention and could spend real time on it. That freed-up attention showed up as 3.5× more throughput on the PRs that still required human judgment.
```

### external-code-review-bottlenecks--clean-close

`train` - `approved` - 337 approximate tokens - 211 words

Headings: Costs / What's next

```markdown
## Costs

Across a 14-day sample, our automated code reviews consumed an estimated $3.57 in LLM usage per attempt. That’s more than a lightweight review bot but substantially less than premium managed multi-agent review (e.g. Anthropic’s managed code review), while buying two independent frontier-model assessments and a separate synthesis pass.

Our internal system is also connected to OpenCode and we can relatively straightforwardly swap out any of the reviewer models with other cheaper model types in the future (e.g. Kimi K3 or Qwen3.8). The framework we use allows us to have any number of coding agent reviewers under the orchestrator so this is tunable in the future.

## What's next

The results are early, so we still need to understand how these auto-reviews affect our long term outcomes like bugs shipped, product quality, roadmap speed, etc.

We're continuing to tune the auto-reviewer: categorizing the reviews coming in, identifying common failure patterns, and feeding our recurring failure patterns back into the policy automatically.

Speeding up one stage of a pipeline tends to move the constraint to the next stage. As agents make implementation and review faster, we expect the constraint to move again, maybe to specification, testing, or deciding what's worth building. When it does, we'll continue hill climbing there.
```

### external-code-review-bottlenecks--sentence-001

`train` - `approved` - 21 approximate tokens - 16 words

Headings: (intro or continuation)

```markdown
Speeding up one stage of a pipeline tends to move the constraint to the next stage.
```

## Database abstractions for Golang

### external-database-abstractions-golang--001

`test` - `candidate` - 659 approximate tokens - 420 words

Headings: Challenge 1: Writing performant, reusable SQL queries / The problem: Sharing code between single and multi-row getters

```markdown
At [Assembled](http://assembled.com/), we’ve been using Golang as our exclusive backend language since our founding in 2018. We run a pretty standard web application, but we found that accessing the database comes with its own particular set of challenges that haven’t been fully addressed by the Go standard library or community packages.

In this article, we’ll talk about 3 abstractions we’ve built at Assembled that make database access in Golang easier:

*   An interface to share code between single- and multi-row getters
*   A helper method to ensure you’re always handling errors and closing rows when scanning from the database
*   An interface to share code between transactions and non-transactions

## Challenge 1: Writing performant, reusable SQL queries

### The problem: Sharing code between single and multi-row getters

When we first started writing SQL queries, we dutifully wrote raw SQL like many Golang tutorials told us. But we soon ran into problems with this approach. Let’s say you’re writing an e-commerce application, then you might have the following method to get the information for a particular order:

type Order struct {

 ID string

 ItemID string

 Price int

}
func GetOrder(id string) (*Order, error) {

 var order Order

row := db.QueryRow("SELECT id, item_id, price FROM orders WHERE id = $1;", id)

 err := row.Scan(&order.ID, &order.ItemID, &order.Price)

 if err != nil {

 return nil, err

 }

 return &order, nil

}

This is great if you only need to get one order, but what if you want to implement a page where a customer can see all their orders and now you need to add a method to fetch multiple orders? The easiest way to reuse your old code is by getting all the order ids that match and then reusing that original method that you wrote for `GetOrder()`.

func GetAllOrders() ([]Order, error) {

 rows, err := db.QueryRows("SELECT id FROM orders;")

 if err != nil {

 return nil, err

 }

 defer rows.Close()
var ids []string

 for rows.Next() {

 var id string

 if err := rows.Scan(&id); err != nil {

 return nil, err

 }

 ids = append(ids, id)

 }

var orders []Order

 for _, id := range ids {

 order, err := GetOrder(id)

 if err != nil {

 return nil, err

 }

 orders = append(orders, order)

 }

 return orders, nil

}

The problem with the above is that you’re now making `O(# of orders)`queries. This is expensive and non-performant because:

*   Postgres has to parse and generate a query plan for every query
*   You’ll add the packet roundtrip time from your webserver to the database to every request, which can blow up very quickly if you have lots of requests [0].
```

### external-database-abstractions-golang--002

`test` - `candidate` - 556 approximate tokens - 341 words

Headings: The solution: Create an abstraction for scanning a database row

```markdown
### The solution: Create an abstraction for scanning a database row

To solve this problem at Assembled, we introduced an abstraction for scans. The important insight here is to realize that whether you’re scanning a single database row or multiple database rows, you should be performing the same operations. You always want to populate the same fields on an `Order` every time you pull one out of the database (whether you’re fetching one order or multiple). So we created a `Scannable` interface that hides the way in which you’re fetching a database row.

type Scannable interface {

 Scan(dest ...interface{}) error

}
Now, you can pass in either `sql.Row` or `sql.Rows` into a single method and perform the same operation. Here’s an example of how you might use the `Scannable` interface to reuse code:

var orderAttributes = []string{

 "id",

 "item_id",

 "price",

}
func ScanOrder(row Scannable) (*Order, error) {

 var order Order

err := row.Scan(&order.ID, &order.ItemID, &order.Price)

 if err != nil {

 return nil, err

 }

 return &order, nil

}

func GetOrder(id string) (*Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = $1;",

 strings.Join(orderAttributes, ","))

row := db.QueryRow(query, id)

 return ScanOrder(row)

}

func GetOrders(ids []string) ([]Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = ANY($1);",

 strings.Join(orderAttributes, ","))

rows, err := db.Query(query, pq.Array(ids))

 if err != nil {

 return nil, err

 }

 defer rows.Close()

var orders []Order

 for rows.Next() {

 order, err := ScanOrder(rows)

 if err != nil {

 return nil, err

 }

 orders = append(orders, *order)

 }

 return orders, nil

}

Now the total time to run `GetOrders` is just a single roundtrip time to your database plus the time it takes to select your matching orders and return them from Postgres. In addition to the query speed improvements, you’ve reduced the number of database queries to a constant number for each `GetOrders` call and significantly decreased database load. Finally, you’ve also made the code easier to reason about and refactor because there is only a single point of entry when you update an attribute on the `Order` struct.
```

### external-database-abstractions-golang--003

`test` - `candidate` - 614 approximate tokens - 371 words

Headings: Challenge 2: Remembering to close a set of rows / The problem: At some point, you’re going to forget to close your rows / The solution: A helper method where you can’t forget

```markdown
## Challenge 2: Remembering to close a set of rows

### The problem: At some point, you’re going to forget to close your rows

> Nothing is certain, except death, taxes, and forgetting to close your rows.
>
>  — Benjamin Franklin (probably)

One of the nasty things about Golang’s SQL driver is the mandatory call to`rows.Close()` after completion which releases your connection back into your pool. Failure to call this method results in increased latency, escalating connection pool sizes, and in the worst-case scenario, outages during holidays when no one is deploying.

Unfortunately, this is one of the hardest problems to debug if you don’t know what you’re looking for. You have to step through a giant codebase, looking for those places where someone forgot to call `rows.Close()`. Let me tell you — it’s not easy to find these instances.

### The solution: A helper method where you can’t forget

How did we fix this problem at Assembled? We had weekly trainings to remind everyone to never ever ever forget to call `defer rows.Close()` and publicly shamed engineers who still forgot.

Just kidding — we created a better abstraction via the `ScanRows` helper method:

type Rows interface {

 Close() error

 Err() error

 Next() bool

 Scan(dest ...interface{}) error

}
func ScanRows(r Rows, scanFunc func(row Scannable) error) error {

 var closeErr error

 defer func() {

 if err := r.Close(); err != nil {

 closeErr = err

 }

 }()

var scanErr error

 for r.Next() {

 err := scanFunc(r)

 if err != nil {

 scanErr = err

 break

 }

 }

 if r.Err() != nil {

 return r.Err()

 }

 if scanErr != nil {

 return scanErr

 }

return closeErr

}

Notice that `ScanRows` will always close the rows after it’s finished with them. The function has an added convenience benefit too: it contains error handling that previously was copy pasted over and over again by every engineer.

Here’s how it would work in our `GetOrders` function:

func GetOrders(ids []string) ([]Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = ANY($1);",

 strings.Join(orderAttributes, ","))
rows, err := db.Query(query, pq.Array(ids))

 if err != nil {

 return nil, err

 }

var orders []Order

 err := models.ScanRows(rows, func(row Scannable) error) error {

 order, err := ScanOrder(rows)

 if err != nil {

 return err

 }

 orders = append(orders, *order)

 return nil

 })

 if err != nil {

 return nil, err

 }

return orders, nil

}
```

### external-database-abstractions-golang--004

`test` - `candidate` - 680 approximate tokens - 418 words

Headings: Challenge 3: Reusing queries inside of transactions / The problem: Sharing SQL between transactions and non-transactions

```markdown
## Challenge 3: Reusing queries inside of transactions

### The problem: Sharing SQL between transactions and non-transactions

Let’s say you just wrote a method to store an `Order` into your database:

func StoreOrder(db *sql.DB, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

There are a couple of ways you might want to call this method:

1.   Use `StoreOrder` directly. For example, if you’re syncing orders from Stripe
2.   Use `StoreOrder` in conjunction with other database methods. For example, if someone makes a purchase on your site, you want to store both payment information and order information at the same time

In case 1, you don’t want to store orders in a transaction — long running transactions can be bad for database performance, so you can simply use your `StoreOrder` method that you’ve already written. But in case 2, you do want to store your order in a transaction, so you have to add some additional code. Here’s what it ends up looking like:

func StoreOrder(db *sql.DB, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

func StoreOrderTx(tx sql.Tx, order Order) (*Order, error) {

 _, err := tx.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }

return nil

}

func SyncOrderFromStripe(db *sql.DB, stripeID string) (*Order, error) {

 stripeOrder, err := stripeClient.Get(stripeID)

 if err != nil {

 return err

 }

 order := Order{ItemID: stripeOrder.Items[0].ID, Price: stripeOrder.Amount}

 return StoreOrder(db, order)

}

func StoreOrderAndPayment(db *sql.DB, order Order, payment Payment) (*Order, *Payment, error) {

 tx, err := db.Begin()

 if err != nil {

 return nil, nil, err

 }

storedOrder, err := StoreOrderTx(tx, order)

 if err != nil {

 return nil, nil, err

 }

 storedPayment, err := StorePaymentTx(tx, payment)

 if err != nil {

 return nil, nil, err

 }

err = tx.Commit()

 if err != nil {

 return nil, nil, err

 }

 return storedOrder, storedPayment, nil

}

Notice that you have to basically copy everything inside of `StoreOrder` into `StoreOrderTx` with the only difference being that in the former you run the method on `sql.DB` whereas in the latter you run it on `sql.Tx`.

This is a lot of unfortunate code copying, and if you change any attribute in `Order`, you have to remember to update both `StoreOrder` and `StoreOrderTx`. And let’s face it, at some point someone is going to forget and cause a bug.
```

### external-database-abstractions-golang--005

`test` - `candidate` - 452 approximate tokens - 258 words

Headings: The solution: Interface for database-like objects and a helper for transactions

```markdown
### The solution: Interface for database-like objects and a helper for transactions

Instead of copying code, notice that the `StoreOrder` method doesn’t really care whether it’s operating on `sql.DB` or `sql.Tx`, it just cares that it can write to the database. This is a perfect time to bring in the `Database` abstraction to hide this away:

type Database interface {

 Query(query string, args ...interface{}) (*sql.Rows, error)

 QueryRow(query string, args ...interface{}) *sql.Row

 Exec(query string, args ...interface{}) (sql.Result, error)

}
Now you can delete your `StoreOrderTx` method because both `sql.DB` and `sql.Tx` will implement the `Database` interface, which can greatly simplify your code:

func StoreOrder(db Database, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

func SyncOrderFromStripe(db *sql.DB, stripeID string) (*Order, error) {

 stripeOrder, err := stripeClient.Get(stripeID)

 if err != nil {

 return err

 }

 order := Order{ItemID: stripeOrder.Items[0].ID, Price: stripeOrder.Amount}

 return StoreOrder(db, order)

}

func StoreOrderAndPayment(db *sql.DB, order Order, payment Payment) (*Order, *Payment, error) {

 tx, err := db.Begin()

 if err != nil {

 return nil, nil, err

 }

storedOrder, err := StoreOrder(tx, order)

 if err != nil {

 return nil, nil, err

 }

 storedPayment, err := StorePayment(tx, payment)

 if err != nil {

 return nil, nil, err

 }

err = tx.Commit()

 if err != nil {

 return nil, nil, err

 }

 return storedOrder, storedPayment, nil

}

The `Database` abstraction allows you to create methods for storing and getting from the database that don’t care whether they’re used in a transaction or not.
```

### external-database-abstractions-golang--006

`test` - `candidate` - 370 approximate tokens - 244 words

Headings: Conclusion

```markdown
## Conclusion

We came up with a set of abstractions that solve some common problems we’ve run into while running Golang and PostgreSQL in production. The abstractions are pretty simple, but they’ve saved us a ton of headaches in production and made it much easier to reason about the code we write.

If you’re interested in building on top of these abstractions (or creating more of them), reach out to me at john@assembled.com or check out our careers page: [https://www.assembled.com/careers-at-assembled](https://www.assembled.com/careers-at-assembled).

[0]: It’s especially expensive if your web server and your database aren’t co-located — this was the case for Assembled in some cases as we started to build out a more global infrastructure. If the query to select your matching order ids takes 100ms and if it takes 30ms to round trip from your webserver to your database, and let’s say it takes 10ms to fetch a single order from Postgres, then a measly 30 orders will take `(30ms + 100ms) + (30ms + 10ms)*30 = 1.3s`. That’s unacceptable performance for most self-respecting e-commerce applications. Of course, you can always try to colocate your webserver and your database in the same datacenter, but that has its own set of problems. In addition, you’d still be making `O(# of orders)`separate database connections which can very quickly cause degraded database performance if you’re not careful.

Many thanks to Anthony Duong and Ryan Wang for reading drafts of this.
```

## Your LLM provider will go down, but you don't have to

### external-llm-provider-fallbacks--001

`dev` - `candidate` - 472 approximate tokens - 274 words

Headings: Manual switchovers (and why they don’t work)

```markdown
LLM providers are famously unreliable. When writing this article, I took a look at OpenAI and Anthropic's status pages, and they reported 99.80% and 99.58% uptime respectively over recent months. This translates to over **3 hours of potential downtime per month** — an eternity when you're powering customer-facing features.

At Assembled, we've adopted Stripe's philosophy: we get to choose our own vendors, so we’re responsible for downtime regardless of which vendor caused the failure.

Before implementing automated fallbacks, we experienced multiple customer-impacting outages. These incidents were particularly frustrating because there wasn't much we could do in real-time other than manually switch models — a process that could take precious minutes during an active outage.

These experiences taught us that reactive fixes weren't enough. We needed an engineering approach that builds resilience into the architecture from the start.

## Manual switchovers (and why they don’t work)

Our first attempt at handling provider outages involved on-call engineers manually switching providers during outages with an easily accessible configuration. Though clever, this ultimately failed because:

*   **Multiple providers per use case**: We use a variety of different models and are constantly swapping in new models, so blanket switches broke our nuanced routing.
*   **Response delays**: Even with good procedures, manual switchovers often took several minutes and caused stress for the on-call engineer.
*   **Poor outage classification**: It was hard for humans to quickly distinguish between full outages and transient issues, meaning judgment calls would have to be made for elevated error rates that didn’t take a provider fully down.

The manual approach taught us that we needed automation, but it also revealed the complexity that our automated system would need to handle.
```

### external-llm-provider-fallbacks--002

`dev` - `candidate` - 251 approximate tokens - 107 words

Headings: Building automated fallbacks / Model categories

```markdown
## Building automated fallbacks

To combat these problems, we designed a very simple automated fallback system that maintains separate ordering preferences for different model categories. This enabled instant failovers when providers become unavailable.

### Model categories

First, we organized our models into categories based on their intended use cases.

type ModelCategory string

const (
Fast ModelCategory="fast"
Smart ModelCategory="smart"
Reasoning ModelCategory="reasoning"
)

func GetModelForCategory(category ModelCategory, platform ModelPlatform) ModelType {
switch platform {
case ModelPlatformOpenAI:
switch category {
case Fast: return ModelTypeGPT4_1_Mini
case Smart: return ModelTypeGPT4_1
case Reasoning: return ModelTypeO_3
}
case ModelPlatformAnthropic:
switch category {
case Fast: return ModelTypeClaude3_5_Haiku
case Smart: return ModelTypeClaude4_Sonnet
case Reasoning: return ModelTypeClaude4_Opus
}
// ... additional platforms
}
return ModelTypeGPT_4_1// sensible default
}
```

### external-llm-provider-fallbacks--003

`dev` - `candidate` - 402 approximate tokens - 206 words

Headings: Provider ordering and fallback logic

```markdown
### Provider ordering and fallback logic

Then we established a global provider ordering that determines our fallback sequence when the primary model fails:

var GlobalFallbackOrder= []ModelPlatform{
ModelPlatformOpenAI, // Primary choice
ModelPlatformAnthropic, // Secondary
ModelPlatformGemini, // Tertiary
}

The fallback logic maintains model category consistency across providers. If GPT-4.1-Mini fails, we fall back to Claude 3.5 Haiku (both "Fast" category), then Gemini 2.5 Flash. This ensures users get equivalent capability levels regardless of which provider ultimately handles the request.

We also provided configurable timeouts for each LLM request to cancel a request after a certain amount of time.

Once we established fallback ordering and categories, the implementation was relatively straightforward: listen for an error or a timeout, then try the next model in that category.

func (agent*LLMAgent) CreateCompletion(ctx context.Context, request*CompletionRequest) (*Response, error) {
// Build list of primary model + fallbacks for same category
modelsToTry:= []ModelType{agent.primaryModel}
for _, platform:=range GlobalFallbackOrder {
if platform!=agent.primaryPlatform {
fallbackModel:=GetModelForCategory(agent.category, platform)
modelsToTry=append(modelsToTry, fallbackModel)
}
}

// Try each model in order until one succeeds
var lastError error
for i, model:=range modelsToTry {
response, err:=agent.callSingleModel(ctx, request, model, agent.getModelTimeout())
if err==nil {
return response, nil
}
lastError=err
}

return nil, fmt.Errorf("all models failed: %w", lastError)
}
```

### external-llm-provider-fallbacks--004

`dev` - `candidate` - 551 approximate tokens - 313 words

Headings: Handling streaming responses / Benefits of our simple fallback approach

```markdown
### Handling streaming responses

Streaming adds one key complexity: once we start sending tokens to a user, we can't easily retry with a different model since you may be in the middle of a response (and restarting the stream would cause awkward end user results). Luckily, we found that most outages happen before the first token is returned, so we only attempt a fallback if streaming hasn't yet begun:

func (agent*LLMAgent) StreamCompletion(ctx context.Context, request*CompletionRequest, tokens chan<-Token) error {
modelsToTry:=agent.getModelsToTry()

for i, model:=range modelsToTry {
hasReceivedFirstToken, err:=agent.tryStreamSingleModel(ctx, request, model, tokens, agent.getModelTimeout())

if err==nil {
return nil// Success
}

// Only retry if we haven't started streaming and have more models to try
if!hasReceivedFirstToken&&i<len(modelsToTry)-1 {
continue// Try next model
}

return err
}
}

## Benefits of our simple fallback approach

**Instant failover**: Our system detects failures and switches providers within milliseconds, eliminating the 5+ minute manual switchover delays that previously caused customer-visible outages.

**Automatic handling of partial degradations**: This benefit surprised us. Many LLM providers experience transient errors where a small but non-trivial percentage of requests fail — maybe 2–5% over a 10-minute window. We'd also see increases in failures grouped together, but it wouldn't be enough for us to justify a manual switchover. These partial degradations are now handled automatically by the same logic that handles full-scale outages.

**Hybrid approach for optimization**: We still have the ability to perform manual switchovers of our main model provider, but now it's more of a latency or quality optimization rather than an emergency response to keep us operational.

During a recent multi-hour LLM provider outage, customers experienced near-zero impact with request failure rates below 0.001% — all thanks to automated failover. More importantly, we've eliminated the stress and urgency of emergency manual failovers. Our on-call engineers can focus on building new features rather than frantically switching configurations during outages.
```

### external-llm-provider-fallbacks--005

`dev` - `candidate` - 570 approximate tokens - 331 words

Headings: The cost of redundancy: More evals / Results and lessons learned

```markdown
## The cost of redundancy: More evals

Automated fallbacks significantly improved reliability but introduced new quality challenges. We can no longer evaluate prompts against a single model — we have to ensure consistent quality across the entire fallback chain.

Our evaluation burden increased quite significantly as every prompt change requires evaluation against at least the first two providers in our fallback sequence. This expanded evaluation added 20–30% to our prompt development time.

However, the change has pushed us to invest more in our LLM-as-a-judge tooling so that we can more easily evaluate results across providers in an automated way — something we'll be diving deeper into in an upcoming blog post. Since secondary providers are not hit that often and used as fallbacks, we don’t need a full human evaluation on those fallback providers prompts.

## Results and lessons learned

Since implementing automated fallbacks, we've seen dramatic improvements in system reliability:

*   **99.97% effective uptime** on our AI model responses despite multiple provider outages
*   **Average failover time reduced** from 5+ minutes to hundreds of milliseconds
*   **Zero manual interventions** required during provider outages

The hybrid approach has proved particularly valuable. We maintain the ability to manually adjust provider orderings for performance optimizations, but these changes now enhance our service rather than serve as emergency responses to outages.

Perhaps most importantly, we've learned that treating vendor reliability as a solvable engineering problem (rather than an external dependency we can't control) leads to more robust and customer-friendly solutions. Our customers shouldn't have to care which LLM provider is having issues on any given day. Building reliable systems on top of unreliable dependencies is both good engineering and essential for maintaining customer trust.

_We're always working on making our systems more robust and our customer experiences more reliable. We’re working on everything from AI voice agents to knowledge processing pipelines to customer-facing automation tools. If you're interested in helping us solve these kinds of challenges,_[_check out our open roles_](https://www.assembled.com/careers)_._
```

## How we Built Assembled's New Products Team

### external-new-products-team--001

`test` - `candidate` - 647 approximate tokens - 436 words

Headings: Talk to users

```markdown
Four months ago, we embarked on a journey to create a new AI-powered product at [Assembled](https://www.assembled.com/). While there are many ways to launch a new product at a Series-B company, we decided to create a “startup within a startup” and put the team through a modified version of [YCombinator](https://www.ycombinator.com/) (YC). We had 3 months of intense building and a demo day at the end. Though we knew these initiatives don’t always pan out, I wanted to recreate the early startup atmosphere that I had experienced when founding Assembled in 2018 and when I was a [YC founder](https://www.linkedin.com/in/johnjianwang/) back in 2014.

So we formed the New Products Team to build something that enhanced the efficiency of customer support agents. Here’s how we approached our mission:

The New Products Team at work in “the dungeon”. Kaytlin made sure we hung up the “Live, laugh, love” sign.

## Talk to users

A classic YC mantra says that the two most important tasks at a small startup are to [**write code and talk to users**](https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice)**.** We took that to heart, especially the “talk to users” part.

Since we’re building for support teams, we focused really heavily on listening and interacting with support agents and managers. We’ve done many dozens of shadowing sessions where we watch a support agent work. These shadow sessions really enhanced our knowledge of agent workflows, but there’s still a barrier of observability where you’re not actually on the hook to finish out a support ticket and you don’t have to deal with the consequences of your replies.

That’s why we also do support takeovers: our team of 4 takes full responsibility of support for a few days and relieves the Assembled customer support team so they can work on other projects. These sessions really helped hone our thinking of what it’s like to literally be a support agent.

By being the backstop for Assembled customers, we started to understand small intricacies about a support agent’s day to day that would be difficult observe passively. It’s hard to fathom how much context switching support agents do until you actually run into a ticket that requires the internal admin dashboard, the metrics dashboard, a help center article, and 3 other tabs open to solve. It’s also hard to understand the cognitive load it takes to write an empathetic reply until you spend 5 minutes rewriting the last paragraph over and over again.

The team talking to users: we’re very heavy on our usage of hand gestures and phone booths.
```

### external-new-products-team--002

`test` - `candidate` - 491 approximate tokens - 337 words

Headings: One room, one team

```markdown
## One room, one team

A core belief we held throughout our time was that everyone on the team would be in person, 5 days a week. We ended up commandeering a conference room for the team and we set up a little pod of desks. We even bought a professional sound system with an amplifier to blast electronic music as we were working [0]. We nicknamed it “the dungeon.”

The dungeon did a few things for us:

*   **It made changes in direction easier and faster.** Early in our journey, we were making micro-pivots to our strategy every few hours. One hour, we’d be working on a settings page, and the next hour, we’d realize we didn’t really need that setting to be customer visible, so we’d only make it a backend configuration. We were also making larger pivots to strategy every few days. For example, should we investigate that sales use case that came up in our call? Being in person let us brainstorm and adapt quickly to new information and ideas, especially since our strategy was constantly shifting.
*   **It helped separate us from the rest of the company.** Everyone on the team had expertise in Assembled’s core product of workforce management. However, we needed space to think deeply about our new product, and our separate room helped make clear that we were focusing on a new problem and allowed us to set more specific times on when we’d work on Assembled’s core product.
*   **Most importantly, it was way more fun.** There’s something magical about working and goofing off late into the night in a small room. It makes you feel really connected to the people you’re working with. Disagreements were addressed more candidly, ideas were shared more freely, and the team grew closer. This connection translated into a more cohesive vision and execution of our goals, making “the dungeon” not just a place, but a symbol of our team’s identity and mission.

Jason and Nelson discussing data science techniques. More keyboards mean we can ship faster.
```

### external-new-products-team--003

`test` - `candidate` - 496 approximate tokens - 342 words

Headings: Existential crisis? That’s a feature, not a bug

```markdown
## Existential crisis? That’s a feature, not a bug

On our fourth day working together, I made an announcement to the team: what we were doing wasn’t working. We had started out writing code 12 hours a day based on a cool prototype. This prototype wowed our executives, so we jumped into building a real version. But I realized that we had already broken the first rule of startups: you have to build something people want.

We hadn’t yet validated the problem and we hadn’t spoken to users about what their problems were. So we went back to the drawing board and focused exclusively on booking user interviews. We ended up doing ten user interviews the next week. Happily, three of these turned into sales calls and would eventually be our first three users.

Another existential crisis occurred the week after we had launched to two large teams. During launch week, we saw all of our metrics skyrocket — we were hitting all time highs for number of power users, messages sent, and daily actives. But the week after, usage dropped like a ton of bricks. We sat down as a team and tried to introspect what had gone wrong. We realized that this skyrocketing usage was merely people testing our product, and we still weren’t sticky enough to keep users. We needed to keep adding functionality and value before we could keep these users, so we threw out our plans to make it easier to onboard onto the product, and instead focused exclusively on making the product itself more valuable for existing users.

We continued to have many more existential crises. In fact, if we went a week or two without one, we’d start to get worried and introspect if we were being honest enough with ourselves. These existential crises are a feature of startups though — you only lose your existential angst once you find product market fit and a repeatable business model. By design, we were always questioning whether our product provided sufficient value and always introspecting how to add more value.
```

### external-new-products-team--004

`test` - `candidate` - 509 approximate tokens - 343 words

Headings: Tuesday dinners

```markdown
## Tuesday dinners

Our YC-inspired approach extended to extracurriculars as well. Every Tuesday night, we would invite folks like [Dan Robinson](https://www.linkedin.com/in/dan-robinson-a6930726/) (ex-CTO of Heap), [Josh Ma](https://www.linkedin.com/in/joshmaa/) (ex-CTO of Benchling), [Harry](https://www.linkedin.com/in/harry-z-yu/) and [Peter Xu](https://www.linkedin.com/in/pxpeterxu/) (co-founders of Wanderlog) to grab dinner with us and share their startup journey and the mistakes they’d made along the way. That said, even though we had quite a few illustrious people come chat with us, the dinners I enjoyed the most were the ones where we had failed to find a speaker and instead went out to eat as a team.

I remember one night, we went to an Indian restaurant, ordered gobs of food, and talked about what we wanted in life. Each person had a different motivation. One team member grew up in a world with adults telling him he wouldn’t amount to much. Because of his early experience, he became hyper competitive and wanted to prove everyone wrong. One team member was a true non-conformist and wanted to carve her own path. Yet another team member wanted to be constantly challenged and was scared of ever being too comfortable.

While everyone had a different reason for being on the team, all of our motivations were deeply rooted and had nothing to do with career progression or resume padding. We were quite far from what you would describe as folks who wanted conventional success. Each of us had a chip on our shoulder in our own way, and this bound us together in our desire to craft something meaningful.

If you’re interested in joining the team, we’re looking for a few hungry, product oriented engineers. You can apply on our careers page [https://www.assembled.com/careers-at-assembled](https://www.assembled.com/careers-at-assembled) or shoot me an email at john@assembledhq.com if you want to chat more.

Thanks to Anthony Duong, Brian Sze, Kaytlin Louton, and Ryan Wang for reading drafts of this article.
```

## Product lessons from Dan Robinson, ex-CTO of Heap

### external-product-lessons-dan-robinson--001

`train` - `candidate` - 258 approximate tokens - 174 words

Headings: (intro or continuation)

```markdown
At [Assembled](https://www.assembled.com/), we’ve made it our mission to have a culture of continuous learning. We’ve been inviting the best minds from the startup space to share their wisdom on building successful products. A few weeks ago, we had the privilege of hosting [Dan Robinson](https://www.linkedin.com/in/dan-robinson-a6930726/) for a dinner discussion.

Dan was one of the first engineers at [Heap](https://www.heap.io/) and served as its CTO for almost 9 years. He helped Heap scale to more than 350 employees and a $110M Series D funding round, so he’s in the unique position to have seen a company scaling at many different points of growth.

Here were some of the top takeaways from the discussion:

*   **Execution, execution, execution:** Most businesses come down to how well you can make a product that matches your user’s needs
*   **Talk to your users with intellectual honesty**: Be careful with leading questions that can bias your users
*   **Taste the soup:** Try out your own product as often as you can
```

### external-product-lessons-dan-robinson--002

`train` - `candidate` - 294 approximate tokens - 209 words

Headings: The Burnt Pizza Problem

```markdown
## The Burnt Pizza Problem

> You need to determine whether the pizza is burnt (e.g. did you execute poorly) or if the pizza was a bad idea.

The default state for early stage startups is to have low, inconsistent usage. Thus, one of the most important jobs of anyone at a startup is to diagnose low usage and identify strategies for increasing it.

Dan uses the Burnt Pizza paradigm as one way to think through this. Let’s say you’re experimenting with a new food and you give your test users burnt pizza. They don’t like it. Was pizza a bad idea or was the problem that it was burnt? Whenever Heap shipped a feature that got weak usage, the right question was: “were we wrong about the user need or did we do a bad job solving it?”

What I found most interesting about this paradigm is that often many of the best companies have ideas that are very similar to a myriad of other competitors. Facebook, Myspace, and Friendster famously had very similar ideas for their offerings. However, Facebook grew into a generational company by focusing on execution of viral features and moving very quickly. They didn’t “burn the pizza” but instead focused on listening to their users.
```

### external-product-lessons-dan-robinson--003

`train` - `candidate` - 464 approximate tokens - 329 words

Headings: Talk to users, but in a specific way

```markdown
## Talk to users, but in a specific way

Which brings us to the next topic: how to listen to your users. YCombinator famously says [you should only do two things](https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice) at your startup: “write code [and] talk to users.” However, it’s really hard to talk to users in the right way and not bias them in the wrong ways.

Dan mentioned there was a product at Heap that didn’t work out. Heap had many internal meetings about how to build this product and how it would fit into Heap’s future strategy, and only once most of this had been figured out did they talk to customers.

This led to customer conversations like: “If you could have X, would you use it?” or “Do you think X is a good idea?” These questions are predisposed to cause your users to say nice things to you. A user can always say “yes, I’d use it” but they don’t have any skin in the game. You’re also not getting any useful information on how valuable your product is.

For Heap’s next product launch (which was much more successful), Dan ensured the team got very precise about how they would learn about what users wanted. He asked questions like “How would you articulate the value of this product to your teammate?” (helps you identify how the user thinks about the value of the product) and “what have you already done to solve your problem?” (helps determine how much of a problem it really is). He also asked for pilot users to pay, which is the true determiner of how valuable a product is.

Ultimately, Dan said this all came down to **intellectual honesty**. The best way to build a useless product for months is by letting your excitement influence the conversations you have with users. Instead, you should focus on trying to be as unbiased as possible on the most important problems that users are actually facing.
```

### external-product-lessons-dan-robinson--clean-close

`train` - `approved` - 299 approximate tokens - 205 words

Headings: Create a culture of product learning and product focus

```markdown
## Create a culture of product learning and product focus

Dan recounted a story of Heap’s goal to have every single employee “taste the soup”. For the quarter, every single Heap employee (from engineers to salespeople to HR folks) was required to engage with the Heap product. Dan mentioned that the night before the deadline, he and the CEO were furiously direct messaging folks on Slack making sure they would finish this requirement.

I found that anecdote fascinating: here’s a CTO of a 200+ person company going out of his way to create a culture of product focus. When asked why, Dan pointed out that it’s relatively easy for the entire team to have a deep understanding of the product in the early days of a startup. However, as Heap expanded, maintaining this depth of knowledge and empathy with users became harder and harder. Therefore, a sustained focus on the product became even more crucial — it was the only way to get everyone aligned on how to create a great product.

Dan closed with this: startups ultimately have to build something that people find valuable enough to pay money for. It’s one of the most basic observations, but often the basic things are the most important.
```

## Scaling LLMs with Golang: How we serve millions of LLM requests

### external-scaling-llms-golang--001

`train` - `candidate` - 689 approximate tokens - 353 words

Headings: Type safety and structured outputs

```markdown
While the LLM ecosystem is overwhelmingly Python-first, we've found Go to be exceptionally well-suited for production deployments. Our Go-based infrastructure handles millions of monthly LLM requests with minimal performance tuning. Beyond Go's well-documented advantages (see Rob Pike’s excellent [distillation of Go's benefits](https://go.dev/talks/2012/splash.article)), three capabilities have proven particularly valuable for LLM workloads: static type checking for handling model outputs, goroutines for managing concurrent API calls, and interfaces for building composable response pipelines. Here's how we've implemented each of these in our production stack.

## Type safety and structured outputs

One of the main challenges with LLMs is handling their unstructured outputs. OpenAI's [structured output support](https://platform.openai.com/docs/guides/structured-outputs) has been a significant advancement for us, and Go's type system makes it particularly elegant to implement. Rather than writing separate schema definitions, we can leverage Go's struct tags and reflection to generate well defined schemas. Here’s an example where we automatically convert a `SupportResponse` into OpenAI's JSON schema format using the [go-openai](https://github.com/sashabaranov/go-openai) library:

import (
"github.com/sashabaranov/go-openai"
"github.com/sashabaranov/go-openai/jsonschema"
)

type SupportResponse struct {
Answer string`json:"answer"`
RelatedDocs []string`json:"related_docs"`
}

func GetSupportResponse(messages []openai.ChatCompletionMessage) (*SupportResponse, error) {
var supportResponse SupportResponse
schema, err:=jsonschema.GenerateSchemaForType(supportResponse)
if err!=nil {
return nil, err
}

resp, err:=client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{
Messages: messages,
ResponseFormat: &openai.ChatCompletionResponseFormat{
Type: openai.ChatCompletionResponseFormatTypeJSONSchema,
JSONSchema: &openai.ChatCompletionResponseFormatJSONSchema{
Name: "support_response",
Schema: schema,
Strict: true,
},
},
})
if err!=nil {
return nil, err
}
err=schema.Unmarshal(resp.Choices[0].Message.Content, &supportResponse)
if err!=nil {
return nil, err
}
return&supportResponse, nil
}

The above code will provide us with `Answer` and `RelatedDocs` populated directly from an LLM call. Now, the `SupportResponse` can be easily passed to our frontend or saved in our database.

Notice that because Golang has a type system built in, you don’t have to spend any extra time defining the object structure ([like you would in Python](https://platform.openai.com/docs/guides/structured-outputs#how-to-use)) — it’s already available via reflection and you can spend more of your time on prompting, inputs, and outputs of the LLM.
```

### external-scaling-llms-golang--002

`train` - `candidate` - 399 approximate tokens - 212 words

Headings: Parallel processing and latency

```markdown
## Parallel processing and latency

LLM applications often require concurrent API calls and complex orchestration. Go's goroutines and channels make this remarkably straightforward.

For instance, suppose we're running a Retrieval Augmented Generation (RAG) pipeline and want to perform hybrid search across three different search backends (see our article on [Better RAG Results with Reciprocal Rank Fusion and Hybrid Search](https://www.assembled.com/blog/better-rag-results-with-reciprocal-rank-fusion-and-hybrid-search)). Running these searches serially would add up their individual latencies, resulting in slower responses. With Go we can relatively easily parallelize searches across multiple backends:

func ParallelSearch(query string) []SearchResult {
ctx, cancel:=context.WithTimeout(context.Background(), 750*time.Millisecond)
defer cancel()

resultsChan:=make(chan []SearchResult, len(backends))
var wg sync.WaitGroup

for _, backend:=range backends {
wg.Add(1)
go func(backend func(string) ([]SearchResult, error)) {
defer wg.Done()
results, err:=backend(query)
if err!=nil {
return
}
select {
case resultsChan<-results:
case<-ctx.Done():
}
}(backend)
}

wg.Wait()
close(resultsChan)

var combined []SearchResult
for res:=range resultsChan {
combined=append(combined, res...)
}

return combined
}

This pattern reduces our total latency to that of the slowest backend, with a configurable timeout to prevent any single slow backend from bottlenecking the entire system. The results are collected via a Go channel and combined after all the Goroutines have completed or timed out.
```

### external-scaling-llms-golang--003

`train` - `candidate` - 496 approximate tokens - 275 words

Headings: Response processing pipeline

```markdown
## Response processing pipeline

LLM outputs often need multiple transformations before they're ready for end users. For example, if you're using an LLM provider with great reasoning ability but doesn't yet have structured outputs (e.g. Claude 3.5 Sonnet), you'll likely want to structure the output in your prompt and parse the output before passing it to an end user.

We've built a composable pipeline that makes these transformations both maintainable and testable:

type ResponseCleaner interface {
Clean(context.Context, string) (string, []ResponseDetails, error)
}

type ResponseDetails struct {
DetailType string`json:"detail_type"`
Content interface{} `json:"content"`
}

Each cleaner is a discrete unit that handles one specific transformation. This separation of concerns makes testing straightforward and allows us to modify individual transformations without touching the rest of the pipeline. Here's how we handle source citations:

type CitedSourceCleaner struct{}

func (c CitedSourceCleaner) Clean(ctx context.Context, message string) (string, []ResponseDetails, error) {
sourceRegex:=regexp.MustCompile(`\[(Source|Ref):\s*([^\]]+)\]`)
var citations []ResponseDetails

matches:=sourceRegex.FindAllStringSubmatch(message, -1)
for i, match:=range matches {
citations=append(citations, ResponseDetails{
DetailType: "citation",
Content: map[string]interface{}{
"number": i+1,
"source": match[2],
},
})
message=strings.Replace(message, match[0],
fmt.Sprintf("[%d]", i+1), 1)
}

return message, citations, nil
}

Using the above cleaner, when an LLM responds with:

> According to [Source: docs/onboarding.pdf] and [Source: kb/troubleshooting.md], the API rate limit is 100 requests per minute for [Source: pricing.pdf] premium accounts.

The cleaner will parse the sources and pass them to the frontend as response details. It will also transform the raw LLM output into:

> According to [1] and [2], the API rate limit is 100 requests per minute for [3] premium accounts.
```

### external-scaling-llms-golang--004

`train` - `candidate` - 425 approximate tokens - 227 words

Headings: Complementing with Python / Conclusion

```markdown
## Complementing with Python

While Go powers our production infrastructure, Python remains essential for ML experimentation and rapid prototyping. The Python ecosystem excels at tasks like:

*   Support ticket clustering with [scikit-learn](https://scikit-learn.org/stable/modules/clustering.html) (for example with [AgglomerativeClustering](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering))
*   Fine-tuning LLMs with transformers (especially [open source models like Llama](https://www.llama.com/docs/how-to-guides/fine-tuning/)), especially for customizing models on our support data
*   RAG prototyping with sentence-transformers to test embedding models and chunking strategies

These tasks would be significantly more complex in Go, where ML libraries are either non-existent or far less mature.

To bridge the Go / Python gap, we maintain a lightweight Python service that our Go infrastructure calls. This service handles computationally intensive ML tasks (like generating embeddings or clustering) while keeping our core infrastructure in Go. In practice, we often prototype features entirely in Python, then gradually port performance-critical components to Go once they're proven. This approach lets us ship improvements incrementally without waiting for a complete Go implementation.

## Conclusion

Go's strengths in type safety, concurrency, and building interfaces have made it an excellent choice for our LLM infrastructure. While Python remains our go-to language for ML development, Go provides the performance and reliability we need in production. The combination of both languages lets us move fast while maintaining a robust, scalable system.
```

## My Startup Journey

### external-startup-journey--001

`train` - `candidate` - 201 approximate tokens - 134 words

Headings: How I “failed” at a YC startup, worked at early Stripe, and then raised $20M

```markdown
## How I “failed” at a YC startup, worked at early Stripe, and then raised $20M

**Lessons (for those who don’t care for my rambling narrative account):**

*   Figure out what great looks like.
*   You have to get lucky, but you also have to capitalize on the lucky opportunities.
*   It’s ok to miss out on your top choice. Your optimization function might be different in a couple of years.
*   It’s hard to spot great businesses, but if you can spot great people to work with, you can narrow the window.
*   Failing gives you better perspective than being told that you will fail.
*   Great engineers aren’t defined by years of experience. They need to care deeply about the product and have the technical prowess to build a great experience.
*   Early decisions at a company have compounding effects.
```

### external-startup-journey--002

`train` - `candidate` - 519 approximate tokens - 363 words

Headings: **Contributing to Ruby on Rails**

```markdown
## **Contributing to Ruby on Rails**

> Lesson: Figure out what great looks like.

In my junior year of MIT, I took a class on open source software. By far my favorite memory was going to an open source conference and meeting [Aaron Patterson (aka Tenderlove)](https://github.com/tenderlove). Aaron is a legend: a member of the Rails core team and an incredibly fascinating person (just take a look at [his website](https://tenderlovemaking.com/) and you’ll understand why). I had never seen someone fix bugs as quickly as him or have such deep knowledge of knowledge of Linux, Rails, and Ruby.

Taking a group photo with Aaron Patterson at an open source conference.

After I met Aaron, I knew I wanted to be just as good as him at programming. So I started contributing to Rails and fixing as many small bugs as I could find. For the next 6 months, I spent my extra hours before class (and during my least favorite classes) working on Rails bug reports. By sheer luck, my first taste of professional software development happened to be on one of the most influential and widely used web frameworks. The core team members held every pull request to a very high standard, and I learned a lot about how to write good code.

> Lesson: You have to get lucky, but you also have to capitalize on the lucky opportunities.

Over the summer, I got assigned to my first big project. I was asked to complete a major refactor of the structure of the Rails application. Unfortunately, [my patch](https://github.com/rails/rails/pull/9655) ran into many issues and never made it into Rails. I learned that making big changes in heavily used code usually leads to bad outcomes (especially when you don’t fully understand a system).

However, I persisted and kept making smaller patches. As the summer came to a close, I had climbed up to become one of the top 50 Rails contributors (to this day, [I’m still in the top 100](https://contributors.rubyonrails.org/contributors/john-j-wang/commits)). But my commits started petering out as the school year started and I began looking for jobs.
```

### external-startup-journey--003

`train` - `candidate` - 590 approximate tokens - 414 words

Headings: Looking for a job in Silicon Valley

```markdown
## Looking for a job in Silicon Valley

> Lesson: It’s ok to miss out on your top choice. Your optimization function might be different in a couple of years.

As I started job hunting, one company stood out amongst all the others: [Meteor](https://www.meteor.com/). I was incredibly excited about Meteor’s team and product. They were a team of ex-Asana engineers building a new open source web framework that automatically pushed database changes out to the frontend. Meteor combined my love of open source software with the new exciting technologies of the time. The only problem was that I didn’t get the job.

I was devastated at the time, but looking back, this ended up being a good thing. I was lucky enough to get job offers from a range of small to large companies. I decided to accept an offer from a little known company called Stripe.

At the time, Stripe wasn’t an obvious choice. My parents had never heard of it, nor had any of my friends (and it would be years before any of my friends had any idea what Stripe did). It was hard to square Stripe’s salary with the money and stability offered at larger tech companies. When I tried to negotiate, I was given the party line: “all engineering salaries are the same.” And I still wanted to work on open source software (ya, I was pretty bummed about Meteor).

I loved the excitement of Silicon Valley and wanted to be a part of it, so I was determined to find a company where I could be a sponge. There were a lot of companies doing exciting things, from big data companies started by world renowned professors to companies producing the next cutting edge frontend web framework. Every startup seemed to be growing. But it became apparent that external factors were lagging indicators of great companies.

> Lesson: It’s hard to spot great businesses, but if you can spot great people to work with, you can narrow the window.

Stripe was ever so slightly different because it had intelligent people doing things with humility and care. Everyone I talked to genuinely cared about their job and about me as a person, and everyone was high powered. I remember being in awe of [Nelson Elhage](https://nelhage.com/) and [Evan Broder](https://ebroder.net/about/) who worked on technology to hot-swap a linux kernel without rebooting. They were always excited to talk about problems and how to solve them.
```

### external-startup-journey--004

`train` - `candidate` - 170 approximate tokens - 111 words

Headings: (intro or continuation)

```markdown
I also remember the care Stripe put into the recruiting process. [Patrick Collison](https://patrickcollison.com/) went on a coffee walk with me, chatting about everything from Stripe’s machinations to acquire a defunct bank to the economic drivers of productivity growth. They introduced me, a random college student, to their investors. I was in awe and quite literally shaking when they had [Michael Moritz](https://en.wikipedia.org/wiki/Michael_Moritz) and [Paul Graham](http://www.paulgraham.com/) do 20 minute chats with me.

In the end, it was the thoughtfulness and drive in Stripe’s culture that set it apart. Many companies had one or the other, but very few had both.
```

### external-startup-journey--005

`train` - `candidate` - 616 approximate tokens - 453 words

Headings: Starting a YC company

```markdown
## Starting a YC company

So there I was, ready to start working at Stripe in the summer, when Max Kolysh (now the CEO of [Dover](http://www.dover.com/)) sat me down for lunch at Chipotle. It was November of my senior year in college and I was excited to spend my last semester learning and not having to care about grades.

I listened intently to Max talk about how he and [Doug Feigelson](https://www.linkedin.com/in/doug-feigelson-95371825/) had gotten into YC to build an API to connect online shopping. I thought the idea was a bit ridiculous, but Max and Doug were incredibly smart, driven, and humble people. I’ve always optimized my environment for learning and being around great people, so next thing I knew I was signing incorporation documents and flying out to Mountain View. I had no idea what I’d do about the Stripe offer come summer, but I would figure it out when the time came.

**Left**: Listening to Paul Graham give a talk just before starting YC. **Middle**: Doug at his typical desk set up. **Right**: Max and Doug talking with other founders at YC’s office in Mountain View.

I packed up a duffel bag of clothes and headed out to Palo Alto to start [Zinc](https://www.ycombinator.com/companies/zinc). During this time, I learned to grind. Each morning, we’d wake up around noon and code until 8pm. We’d eat a quick dinner and go to the gym before returning at 11pm to continue coding until 3 or 4am in the morning. Many people would say we worked too hard, but I loved it. We were doing something exciting and I poured my heart and soul into it.

> Lesson: Failing gives you better perspective than being told that you’ll fail.

However, as YC came to an end, we still hadn’t come up with a real product. We had been instilled with the YC mentality that growth is paramount and we did everything we could to achieve growth. This led us to create a consumer app that lost money on every transaction. YC was a great forcing function for us to focus exclusively on growth, but we didn’t spend enough time figuring out the fundamentals of what we were doing. What’s more, I learned that coding 13 hours a day doesn’t guarantee anything.

These were hard lessons that I’d carry into the future. As we shut down our product, I knew my startup experience was coming to an end. I had already accepted Stripe’s offer and I was going to stay true to my word. So in June of 2014, I had a somber meeting with Max and Doug and went to work for Stripe.
```

### external-startup-journey--006

`train` - `candidate` - 455 approximate tokens - 317 words

Headings: Working at early Stripe

```markdown
## Working at early Stripe

When I started at Stripe, I asked to delay my start date until after a family vacation, but my manager just told me to start sooner and take time off later (Stripe was just shy of 100 employees and moving incredibly quickly). I now had an artificial deadline of one month to ship my first project.

I was assigned to improve email receipts with [Michelle Bu](https://www.linkedin.com/in/michellebu/). We spent the month touching different parts of the Stripe infrastructure and writing a ton of code. Just before launch date, we stayed up the entire night fixing polish items. I remember going to sleep in a phone booth and waking up early in the morning to try to finish out some last edits while Michelle worked on the blog post.

> Lesson: Great engineers aren’t defined by years of experience. They need to care deeply about the product and have the technical prowess to build a great experience.

At an offsite working on something Stripe related.

One of the things that struck me at Stripe was how humble and hardworking people were. Even though Michelle was a veteran of the Stripe codebase, pushed forward a ton of the project, and even wrote the blog post for the launch, she put my name on the final result (amazingly, this post is still up on [Stripe’s blog](https://stripe.com/blog/improved-email-receipts)). I thought that said a lot about her and Stripe in general.

Michelle also taught me that there are different flavors of great engineers. Some great engineers can act like oracles because of their knowledge and experience. Michelle was only one year out of college, but still one of Stripe’s best engineers (in an unsung hero kind of way). She kept standards high, fixed bugs when she saw them, talked to customers to understand problems, and shipped a ton of changes.
```

### external-startup-journey--007

`train` - `candidate` - 423 approximate tokens - 286 words

Headings: Building a profitable, (mostly) bootstrapped business

```markdown
## Building a profitable, (mostly) bootstrapped business

Stripe was doing incredibly well and was on track to be a very special company. It had an electric atmosphere that combined ambition and humility. But after a year and a half, I started longing for something different. Many of my friends were shocked by my decision to work at Stripe, and many were equally shocked when I quit Stripe to return to Zinc. However, I wanted to optimize for learning and I believed I would learn a broader set of skills at a smaller company.

Zinc began to find traction among a very specific niche of users. Before [Plaid](https://plaid.com/) pioneered a similar business model for finance, our team built out a set of APIs to e-commerce websites for a clientele of small businesses selling items on Amazon and eBay. Within a couple of years, we had built a very profitable business making millions of dollars per year with only about $400k in pre-seed funding. We followed the lead of Basecamp who espoused the benefits of work-life balance, small teams, and eschewing venture capital.

> Lesson: Early decisions at a company have compounding effects.

I loved being at Zinc because the feedback loop was extremely fast. We could see how our decisions a couple of months ago affected our current day to day. For example, building our backend in NodeJS with callbacks haunted us for years. Every time we wrote code, we would contribute more cruft to a sprawling callback hierarchy. On the other hand, our investment in our DevOps infrastructure allowed us to cheaply scale thousands of servers across many cloud hosting providers. Every cent we saved in server costs led directly to a dollar in profit.
```

### external-startup-journey--008

`train` - `candidate` - 499 approximate tokens - 317 words

Headings: Applying lessons and learning new ones at Assembled

```markdown
## Applying lessons and learning new ones at Assembled

After a few years, we were in great shape at Zinc. However, I itched to throw myself at even bigger problems and started talking to my brother, [Ryan Wang](https://www.linkedin.com/in/ryanywang/), and my old friend, [Brian Sze](https://www.linkedin.com/in/briansze/). They were leading a team that built internal tools for the support team at Stripe.

Stripe had seen triple digit growth for years, but still cared about a great support experience. Patrick Collison used to invite engineers over to his apartment to help answer support tickets. However, this didn’t scale as volume grew and Stripe increasingly had to rely on a set of outdated tools to manage its support team. We saw that many companies had very similar problems as Stripe and that the support ecosystem was lacking good tools.

I vividly remember our first meeting with GoFundMe’s support team when [Morgan Wood](https://www.linkedin.com/in/morgan-wood-gfm/) showed us a Google Sheet containing thousands of rows, a litany of color-coordinated cells, and multiple people trying to make edits. While we were at their office, someone had made an accidental edit on the spreadsheet and the operations lead, [Jordan Philyaw](https://www.linkedin.com/in/jordanphilyaw/), had to manually recreate the entire sheet. The level of wizardry was amazing, but it was clear that the tooling needed to get better.

Seeing these types of struggles across the industry led Brian, Ryan, and I to start [Assembled](http://www.assembled.com/) to transform and elevate customer support. We recently [raised a $16M Series-A](https://techcrunch.com/2021/03/12/assembled-an-operating-system-for-support-teams-raises-16-6m/) and I’m now applying many of the lessons I’ve learned to creating a long-lasting, impactful company:

**Left**: Assembled’s office in 2018 (e.g. my living room). **Right**: Assembled’s first career fair where we couldn’t even give away free pizza (recruiting is hard).
```

### external-startup-journey--sentence-001

`train` - `approved` - 35 approximate tokens - 23 words

Headings: (intro or continuation)

```markdown
I learned that making big changes in heavily used code usually leads to bad outcomes (especially when you don’t fully understand a system).
```

## Applying the Lessons of Stripe to Customer Support

### external-stripe-customer-support--001

`train` - `candidate` - 211 approximate tokens - 151 words

Headings: Why support is the next payments

```markdown
## Why support is the next payments

When I left Stripe and started a [company in the customer support space](http://www.assembled.com/), most people thought I was crazy: “why would you leave that rocket ship?” But in many ways, Stripe taught me to see the long game and to invest in the opportunities that no one else paid attention to.

Think back to 2010: the Collison brothers saw a massive problem to be solved in an industry that was considered a backwater by most startups. Back then, it was all about the flashy consumer apps, social networks, and buzzy tech, but for Stripe, it was about staying focused on the opportunity no one could see.

I strongly believe there’s a new wave of change coming to the customer support industry and that it has many of the trappings of the payments industry a decade ago. The two are quite analogous:
```

### external-stripe-customer-support--002

`train` - `candidate` - 658 approximate tokens - 382 words

Headings: A massive, growing market

```markdown
## A massive, growing market

> Proactively delighting customers earns trust, which earns more business from those customers, even in new business arenas. Take a long-term view, and the interests of customers and shareholders align.
>
>  — [Jeff Bezos, Founder of Amazon](https://www.sec.gov/Archives/edgar/data/1018724/000119312513151836/d511111dex991.htm)

Customer support is a massive, growing market and a differentiator for the world’s best businesses. Much like payments in 2010, a confluence of macro factors today have led to the growing importance of customer support:

*   **Consumer expectations have shifted.** Amazon changed the way people shop online by opening people’s eyes to what outstanding customer support looks like. Consumers now expect to receive refunds for damaged items, get tracking updates, and have missing items taken care of. Consumers also make purchasing decisions based on the quality of support they receive. In 2020, [Microsoft found](https://clouddamcdnprodep.azureedge.net/gdc/gdcPiLLQw/original?ocid=mkto_eml_EM582302A1LA1) that 90% of consumers use customer support as a factor in whether or not to do business with a company. A decade ago, customer support was hardly a factor in purchasing decisions, but it has now become one of the dominant inputs.
*   **The world is moving online.** The COVID-19 pandemic accelerated the push to drive life online. Online transactions have been trending upwards for years and now account for over 20% of all retail transactions. Anecdotally, the best brands are advancing with online commerce squarely at the forefront of their minds. [Nike met its goal](https://fortune.com/2020/09/23/nike-q1-ecommerce-results-covid-19/) of moving 30% of its total sales online almost 3 years ahead of time.

Graph from From [https://www.digitalcommerce360.com/article/us-ecommerce-sales/](https://www.digitalcommerce360.com/article/us-ecommerce-sales/)

*   **Companies have budget to spend.** There’s a massive amount of money in customer support. In the United States, there are twice as many [customer support agents](https://www.bls.gov/ooh/office-and-administrative-support/customer-service-representatives.htm) as [truck drivers](https://www.bls.gov/oes/current/oes533032.htm). It’s a $105 billion market in the United States alone, and a lot of global spending occurs in Asia and South America. The software industry for customer support is also growing, evidenced by the fact that Salesforce’s customer support product now [brings in more revenue](https://www.saastr.com/5-interesting-learnings-from-salesforce-at-24b-arr/) than its namesake sales product.
```

### external-stripe-customer-support--003

`train` - `candidate` - 696 approximate tokens - 418 words

Headings: Complex, outdated tools and processes

```markdown
In 2010, the world was becoming more digital and Stripe rode on the coattails of the growth in internet businesses. Today, those internet businesses have progressed and must offer superb customer support to stay competitive.

## Complex, outdated tools and processes

> [I was] baffled at how convoluted and awkward [online payments] appeared to be. It seemed like a prevailing ecosystem designed to reduce the number of Internet businesses.
>
>  — [Patrick Collison, CEO of Stripe](https://www.forbes.com/sites/roberthof/2015/08/18/in-conversation-stripe-ceo-patrick-collison-on-the-limitless-potential-of-payments/?sh=6beb2d85126a)

Building a business in 2010 that took payments online was hard. You had to walk into a bank to fill out an application, pay thousands of dollars in fees, and connect a couple of arcane payments gateways. The whole process could potentially take months, which is what Stripe aimed to solve.

Likewise, scaling up your customer support team today is incredibly difficult. Tools like Zendesk and Intercom send messages but they don’t help you manage your team because they’re the communication layer and not the intelligence layer. Most businesses still rely on spreadsheets to manage a labyrinth of remote workers, all of whom have their own preferences and skills. Modern support teams now work across a wide variety of channels and platforms (like chat, phone, Twitter, WhatsApp) and work in different timezones. What’s more, each agent can have different specializations and skills: from answering developer focused support questions for a company like Stripe to figuring out how to refund a transaction on GoFundMe’s website.

Actual industry-leading customer support software. Many solutions are still desktop based and fighting to move onto the “cloud”.

Most industry-leading customer support tools were built for use in call centers, where the dominant worldview is one of command and control. A hierarchy of managers instruct workers how to maximize efficiency, leading to incredibly specific requirements. It’s pretty depressing to visit an actual call center: bathroom breaks are scheduled down to the 3 minute interval, and taking too long would be punished with a lower performance score. Most call center software is sold to Fortune 500 companies, costs millions of dollars per year, and requires a team of people to implement and maintain them. This is the world that has spawned most of the support tooling we see today.

> One of our values is that you should be looking out for each other. Everyone should try to make the lives of everyone else who works [at Slack] a little bit simpler.
>
>  — [Stewart Butterfield, CEO of Slack](https://www.businessinsider.com/slack-ceo-stewart-butterfield-on-company-culture-he-admires-2015-7)
```

### external-stripe-customer-support--004

`train` - `candidate` - 549 approximate tokens - 337 words

Headings: Fundamental infrastructure for the internet

```markdown
Many modern support teams want to scale their operations up, but not by setting up with a cell center with thousands of people. Most fast growing companies don’t see support agents as cogs in a machine, but instead want a system that is rooted in empathetic support. There’s a new era of companies that are pushing for this, and the old tools aren’t ready to handle this shift.

## Fundamental infrastructure for the internet

> The same way that Google exists as a foundational component of the Internet around information retrieval, it felt like there should be such a foundational component for economic infrastructure, and that was sorely lacking.
>
>  — [Patrick Collison, CEO of Stripe](https://www.forbes.com/sites/roberthof/2015/08/18/in-conversation-stripe-ceo-patrick-collison-on-the-limitless-potential-of-payments/?sh=6beb2d85126a)

Payments and customer support are both areas that are fundamental to operating an online business. They are both necessary and a driver of differentiation among companies:

*   **Foundational**. Every single online business needs to accept payments and support its’ customers, there’s no way around it. Imagine buying something online and not having the ability to contact the company about a lost package or a defective product. The concept is very much akin to sending a check through the mail for an online purchase: it may have worked for mail order catalogs in the 1990s, but having no support today would lead to a quick death.
*   **All companies face the same problems.** Everyone uses the same credit card network because payments systems aren’t created for a specific industry. A company selling balloons can use the same system as a company selling enterprise software. Likewise, customer support remains largely the same across different companies. Whether you’re Glossier selling lipstick or Monzo providing banking services, you must forecast incoming support requests, portion it out to the right people, and solve those requests as quickly and accurately as possible. Some requests may take longer or require multiple steps, but the concept of putting people in the right place at the right time remains the same for all businesses.
```

### external-stripe-customer-support--005

`train` - `candidate` - 431 approximate tokens - 277 words

Headings: A hard, non-obvious problem

```markdown
## A hard, non-obvious problem

> Even the smartest, most imaginative people are surprisingly conservative when deciding what to work on. People who would never dream of being fashionable in any other way get sucked into working on fashionable problems.
>
>  — [Paul Graham, Co-founder of YCombinator](http://www.paulgraham.com/fp.html)

Stripe started in a non-obvious place: no one really talked about APIs and few people cared for payments. The sole payments related business in the top 100 most valuable startups in 2010 was TrialPay, valued at [$200 million and sitting at number 58](https://www.businessinsider.com/digital-100#58-trialpay-58). Only the small number of people who had tried starting an online business understood the problem of payments and it wasn’t obvious to the majority of Americans or the even the majority of people in Silicon Valley.

In the same vein, few people in Silicon Valley have expertise in customer support. I’ve heard anecdotally that engineers will literally quit if they have to work on internal customer support tooling because they don’t believe it to be interesting or impactful. Even fewer people in the management of most technology companies have answered a support ticket themselves.

But if you‘ve ever seen a large support team run, you’ll realize that support is both important and ripe for innovation. My cofounders at [Assembled](https://www.assembled.com/) built out the support tools team at Stripe and found massive gains from targeted changes. At first, people laughed at them for working on support tools, but towards the end of their tenure, their small team of 2 people was replaced by a full team of dozens of product managers, engineers, and business people.
```

## How we saved hundreds of engineering hours by writing tests with LLMs

### external-tests-with-llms--001

`train` - `candidate` - 353 approximate tokens - 213 words

Headings: (intro or continuation)

```markdown
At Assembled, engineering velocity is our competitive edge. We pride ourselves on delivering [new features at a fast pace](https://www.assembled.com/whats-new). But how do we maintain quality without slowing down? The answer lies in robust testing. [As Martin Fowler aptly puts it](https://martinfowler.com/bliki/SelfTestingCode.html):

> [Testing] can drastically reduce the number of bugs that get into production… But the biggest benefit isn't about merely avoiding production bugs, it's about the confidence that you get to make changes to the system.
> Martin Fowler

Despite this, writing comprehensive tests is often overlooked due to time constraints or the complexity involved. Large Language Models (LLMs) have shifted this dynamic by making it significantly easier and faster to generate robust tests. Tasks that previously required hours can now be completed in just 5–10 minutes.

We've observed tangible benefits within our team:

*   An engineer who previously wrote few tests began consistently writing them after utilizing LLMs for test generation.
*   Another engineer, known for writing thorough tests, saved weeks of time by using LLMs to streamline the process.
*   Collectively, our engineers have saved hundreds of hours, reallocating that time to developing new features and refining existing ones.

In this blog post, we'll explore how we’ve used LLMs to enhance our testing practices.
```

### external-tests-with-llms--002

`train` - `candidate` - 564 approximate tokens - 343 words

Headings: Leveraging LLMs for testing

````markdown
## Leveraging LLMs for testing

To get started, you'll need access to a high-quality LLM for code generation like OpenAI's o1-preview or Anthropic's Claude 3.5 Sonnet.

Then, you should craft a precise prompt that guides the model to produce the desired output. Here's a sample prompt we've found effective for generating Go unit tests:

```
Help me write a comprehensive set of unit tests in Golang for the following function:

<function_to_test>
// Insert your function code here
</function_to_test>

Here are the definitions of the associated structs used in the function:

<struct_definitions>
// Optionally insert any relevant struct definitions here
</struct_definitions>

Please ensure that:
- The tests use the fixture pattern by defining different test cases in a slice.
- The tests follow Go's testing best practices, including proper naming conventions and code organization.
- Use the `testing` and `require` packages as shown in the example below.
- Cover various scenarios, including normal cases, edge cases, and error handling.

<test_example>
// Include an example of a good unit test from your codebase
</test_example>
```

In this prompt, you need to provide:

*   **Function to test**: Copy and paste the exact code you’re looking to write tests for.
*   **Struct definitions**: Include any relevant definitions that the function uses (especially for any objects that appear in the input or output of the function).
*   **Example of a test suite**: An example of existing tests that reflect your codebase's style and conventions.

Once you’ve dropped this into an LLM and generated a result, you might need to review and refine the generated tests. You should check for compilation issues, add any potential edge cases the LLM missed, and adjust the style to match your codebase conventions. We’ve found that a few iterations of back and forth are sometimes necessary to arrive at an acceptable test suite. Once you’re close enough, just copy and paste the resulting tests back into your codebase.

If you have an AI-assisted code editor like Copilot or Cursor, the principles remain the same; though, because tools can provide context-aware suggestions based on your existing code, you often can get away with less detailed prompts.
````

### external-tests-with-llms--003

`train` - `candidate` - 522 approximate tokens - 263 words

Headings: Example in action

````markdown
## Example in action

Suppose you're building an e-commerce platform and have a function that calculates an order summary. Here's how you might apply the above approach.

```
// Struct definitions
type OrderItem struct {
    ProductID   string
    Quantity    int
    UnitPrice   float64
    Weight      float64 // Weight per unit in kg
    Category    string
}

type OrderSummary struct {
    TotalPrice      float64
    TotalWeight     float64
    ItemsByCategory map[string]int // Category name to total quantity
}

// Function to test
func CalculateOrderSummary(items []OrderItem) OrderSummary {
    itemsByCategory := make(map[string]int)
    totalPrice := 0.0
    totalWeight := 0.0

    for _, item := range items {
        totalItemPrice := float64(item.Quantity) * item.UnitPrice
        totalItemWeight := float64(item.Quantity) * item.Weight

        totalPrice += totalItemPrice
        totalWeight += totalItemWeight

        itemsByCategory[item.Category] += item.Quantity
    }

    summary := OrderSummary{
		    TotalPrice: totalPrice,
		    TotalWeight: totalWeight,
		    ItemsByCategory: itemsByCategory
		}
    return summary
}
```

Using the suggested prompt, we fed this code into ChatGPT o1-preview and, in **just 48 seconds**, it generated a comprehensive test suite that was ready to use straight out of the box. [Here’s the full prompt and results from ChatGPT](https://chatgpt.com/share/671576aa-c914-8000-9458-798e847e3c2c).

You’ll notice that the resulting tests are both comprehensive and well written:

*   The tests cover basically all of the cases that you might think of: empty slices, nil slices, single item, multiple items, items with zero quantity, etc. These test cases are mutually exclusive and collectively exhaustive and cover most of the edge cases a good engineer would think of.
*   Moreover, the resultant code is in the table-driven fixture style that is idiomatic in Go — the exact format that we specified in the initial prompt. The resultant tests even use the `testify/require` library, which is prescribed in the original example.
````

### external-tests-with-llms--004

`train` - `candidate` - 301 approximate tokens - 123 words

Headings: (intro or continuation)

````markdown
```
import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCalculateOrderSummary(t *testing.T) {
	fixtures := []struct {
		Name     string
		Items    []OrderItem
		Expected OrderSummary
	}{
	  ...
		{
			Name: "Multiple items in different categories",
			Items: []OrderItem{
				{
					ProductID: "P1",
					Quantity:  2,
					UnitPrice: 5.0,
					Weight:    0.2,
					Category:  "Books",
				},
				{
					ProductID: "P2",
					Quantity:  1,
					UnitPrice: 100.0,
					Weight:    1.0,
					Category:  "Electronics",
				},
			},
			Expected: OrderSummary{
				TotalPrice:  (2 * 5.0) + (1 * 100.0),
				TotalWeight: (2 * 0.2) + (1 * 1.0),
				ItemsByCategory: map[string]int{
					"Books":       2,
					"Electronics": 1,
				},
			},
		},
		...
	}

	for _, fixture := range fixtures {
		t.Run(fixture.Name, func(t *testing.T) {
			result := CalculateOrderSummary(fixture.Items)
			require.Equal(t, fixture.Expected.TotalPrice, result.TotalPrice, "TotalPrice mismatch")
			require.Equal(t, fixture.Expected.TotalWeight, result.TotalWeight, "TotalWeight mismatch")
			require.Equal(t, fixture.Expected.ItemsByCategory, result.ItemsByCategory, "ItemsByCategory mismatch")
		})
	}
}
```
````

### external-tests-with-llms--005

`train` - `candidate` - 335 approximate tokens - 178 words

Headings: Extending to more complex scenarios

```markdown
## Extending to more complex scenarios

The same approach can be applied to more complex testing scenarios. By adjusting the prompt and providing a different set of baseline test cases, you can generate tests for:

*   **Different programming languages**. It’s relatively straightforward to adjust the prompt for other languages and tailor the results to specific testing frameworks.
    *   [Example: Unit tests for a typescript function that converts roman numerals to integers, using Claude 3.5 Sonnet](https://gist.github.com/wangjohn/418991f0dac46efdd7daab73a87c722b)

*   **Frontend component testing.** You can also extend this to test React components with user interactions and state changes — just make sure your examples capture the libraries you’d use.
    *   [Example: Testing a React dropdown component with Jest and React Testing Library, including user interactions and DOM assertions, using o1-preview.](https://chatgpt.com/share/67191e6b-9b54-8000-b9b0-17fcd391b677)

*   **Integration testing with mocked services.** By changing the test case examples, you can test functions that interact with external APIs by mocking HTTP clients.
    *   [Example: Testing a function that fetches average weather data by mocking a weather API call, using o1-preview.](https://chatgpt.com/share/671942a2-15f8-8000-8815-4dc68f6dd4e8)
```

### external-tests-with-llms--006

`train` - `candidate` - 673 approximate tokens - 431 words

Headings: Considerations

```markdown
## Considerations

At Assembled, we’ve been using LLMs to write tests for a few months now and have seen big boosts in engineering productivity. That said, there are a few considerations to keep in mind as you start using LLMs for test writing:

*   **Iterative refinement**: You may need several iterations to cover missed edge cases or adjust to your codebase standards. Sometimes, the LLMs might generate code that doesn’t compile, so asking the LLM to make adjustments is critical.
*   **Double check your test logic:** While LLMs are pretty good out of the box, they can sometimes get tests wrong. For example, one of our engineers had an experience where the model gave incorrect output because of improper formatting. We insist that all Assembled engineers read and run any LLM-generated tests before merging into production.
*   **Customize your prompt to your specific context**: Our engineers have found that tailoring their prompts can significantly enhance the quality of the generated tests. For example, you might consider specifying your test frameworks (e.g. “Use Jest and React Testing Library for testing this React component.”) or highlighting important edge cases (e.g. “Ensure you include tests for handling null inputs and maximum integer values.”).
*   **Examples matter:** LLMs do their best work when they have a good example of tests to learn from. The engineering team at Assembled has built a large repository of comprehensive and idiomatic tests over time, which makes it easier to use these techniques. Remember that your examples are often your most important way to drive the LLM to do what you want.
*   **Use the smartest models**: Models like o1-preview or Claude 3.5 Sonnet generally provide better results. Since latency isn't a major concern, we tend to use the best available models.
*   **Code structure reflects testability**: If you’re having trouble getting the LLM to construct suitable tests, consider refactoring your code. It’s likely that whatever combination of inputs and outputs you have may be poorly structured or overly complex. You can even ask the LLM to break things up and refactor your code with the same prompting principles discussed above.
*   **Don’t overdo testing**: You generally want to test the functions that have clear input / output and which contain the most important pieces of logic. You don’t need to test that a checkbox is working correctly (unless you’re the maintainer of a component library). Likewise, glue code is tough to test, and writing tests for some pretty straightforward glue code may not be worth it — though you should check on a case-by-case basis (e.g., if that glue code is a very hot codepath).
```

### external-tests-with-llms--clean-conclusion

`train` - `approved` - 81 approximate tokens - 51 words

Headings: Conclusion

```markdown
## Conclusion

Using LLMs to generate comprehensive test suites in minutes has been a game changer at Assembled. It reduces the activation energy to write tests and makes it less likely that engineers skip tests due to time constraints. This has resulted in a cleaner, safer codebase that has increased development velocity.
```

### external-tests-with-llms--sentence-001

`train` - `approved` - 25 approximate tokens - 19 words

Headings: (intro or continuation)

```markdown
Remember that your examples are often your most important way to drive the LLM to do what you want.
```

## Why I code as a CTO

### external-why-i-code-as-a-cto--001

`train` - `candidate` - 528 approximate tokens - 356 words

Headings: What I actually build / Long-horizon experimental projects

```markdown
Many CTOs I know stopped writing code years ago. The conventional wisdom is that as you become more and more senior, the less and less code you write until eventually you’re spending your days in back-to-back meetings.

That’s not how I operate. In fact, here’s what my last 12 months have looked like:

I currently manage no direct reports and ship a lot of code. Not in an “I dabble when I have free time in between meetings” way, but in an “I shipped multiple substantial features last quarter” way.

I think it’s one of the highest-leverage things I do as a technical leader.

## What I actually build

People assume CTOs who code are either working on pet projects that never ship or doing ceremonial code reviews. That hasn’t been my experience. The code I write falls into three pretty distinct categories, each valuable for different reasons.

### Long-horizon experimental projects

The number of people in an organization who can ship and build substantially new things is actually a scarce resource. Organizations are generally organisms built in a way to maintain status quo and scale current products. I've found there are only a handful of people (founders, a few executives, some really high leverage ICs) who are able to generate new products. So pushing new ideas is quite important because they require intentional, sustained effort. Between org structure, roadmap incentives, and limited risk budget, few engineers can take months to pursue ambiguous bets.

I can. And I’m uniquely positioned to take these meaty experimental projects on as I know the customer pain and the architecture well enough to move fast.

I've had my share of duds, but I've also had some huge hits. A recent example: we kept talking about building an AI chat product for our customers. It was clearly valuable, but it felt like a daunting task, and no one on the team had the time and headspace to take it on given their existing commitments. During Thanksgiving break, I just decided to build it and knocked out a prototype. I then worked with the team to productionize it into a multi-million dollar ARR product.
```

### external-why-i-code-as-a-cto--002

`train` - `candidate` - 395 approximate tokens - 263 words

Headings: Critical customer asks that needed to be done yesterday / Bugfixes (the surprising one)

```markdown
### Critical customer asks that needed to be done yesterday

Sometimes a key customer needs something urgently and it becomes a blocker for a major deal or renewal. These situations require someone who can move fast, understands the full system, and can make pragmatic trade-offs.

Instead of pulling an engineer off their current sprint, I can often cut through the noise. I already have the context and I know the stakes.

Last month, we had a million dollar per year customer that came to us with a burning need: they needed full data redaction on one of our integrations for compliance reasons. Our team had considered potentially having the customer build their own integration on top of our API in order to get around this requirement, and scoping it out properly would have required many meetings across product, legal, and engineering. I built and shipped a working version in a day. It wasn’t perfect, but it solved their immediate problem and preserved goodwill with the customer.

### Bugfixes (the surprising one)

People are often shocked by this, but I fix a lot of bugs! And bugfixing is one of my favorite ways to maintain a mental map of our codebase.

When you're hunting down why pagination breaks on the third page of search results, or why WebSocket connections drop after exactly 60 seconds, you traverse huge swaths of the system. You get a visceral understanding of technical debt that's hard to get from code reviews or architecture discussions. This mental map helps me make better decisions about technical investments and where the team should focus.
```

### external-why-i-code-as-a-cto--003

`train` - `candidate` - 294 approximate tokens - 210 words

Headings: Why I code / It keeps me up to date with what actually works

```markdown
## Why I code

That’s what I ship. Here’s why I structure my role this way:

### It keeps me up to date with what actually works

I use Claude Code, Codex, Cursor, and a bunch of other AI tools daily. This experience lets me understand what’s real and what’s bullshit when making strategic decisions about tooling and hiring.

Here’s a recent example: I spent hours this weekend trying to vibe-code a feature that touched a few gnarly integrations, but made way more progress when I finally sat down and wrote it mostly by hand. It wasn’t very much code, but it had to be the exact right logic (terrible for LLMs). On the other hand, I’ve shipped a big feature almost entirely with Claude Code. Knowing where AI shines (crud, tests, boilerplate) and where it fails (precision, system nuance) always beats making decisions based on Twitter hype.

Being in the code also lets me know when to push and when to let off the gas. I can sense when architectures are overly complex or when technical debt is becoming a real problem. I’ve seen managers who rely only on what people tell them, and they can miss a lot. When you’re in the code, you develop an intuition for what’s real.
```

### external-why-i-code-as-a-cto--004

`train` - `candidate` - 471 approximate tokens - 319 words

Headings: Because it’s what I love and what I’m good at / AI tools have changed the leverage I have

```markdown
### Because it’s what I love and what I’m good at

I don’t particularly enjoy building orgs and figuring out people stuff. Engineering management involves navigating interpersonal dynamics, performance reviews, and organizational design. These are crucial functions, but they’re not where my strengths lie.

That’s why we’ve hired great engineering managers and leaders. They’re better at it than I am, and they enjoy it. This lets me focus on the things that I love: building things, solving technical problems, and writing code.

Startups are kind of like a sprinting marathon, so I design my role around the work that keeps me excited and ready to run fast for a long time. That’s how I can continue doing this for years, which matters a lot for the company.

### AI tools have changed the leverage I have

A few years ago, I struggled to find time to code while handling the strategic parts of my job. As the company grew, I was basically stuck in meetings all day, and I was operating outside my zone of genius. It was one of the toughest periods for me professionally.

But modern AI tools have fundamentally changed this equation (especially in the last few months). I’m probably 2–3x more productive than before. These tools haven’t replaced my judgment or technical knowledge, they’ve actually made those skills more valuable.

I can tell an AI tool, “Build a data export that matches the format of our existing CSV exports but includes these three additional fields from the user profile table,” and it’ll generate most of the code correctly because I know exactly what I need and where to find it. An engineer unfamiliar with that part of the codebase would spend quite a lot of time figuring out those details.

The job has shifted from “writing every line of code” to “providing context, making decisions, and evaluating solutions.” And luckily, I have a lot of context.
```

### external-why-i-code-as-a-cto--clean-conclusion

`train` - `approved` - 315 approximate tokens - 195 words

Headings: Figuring out what works for you

```markdown
## Figuring out what works for you

When I was figuring out my role as CTO, I read [Greg Brockman’s blog post](https://blog.gregbrockman.com/figuring-out-the-cto-role-at-stripe) about defining the CTO role at Stripe. He talked to a bunch of other CTOs and realized there’s enormous variance in what the role looks like. Some CTOs are technical visionaries, some are org builders, some are infrastructure-focused. The commonality is that great CTOs figure out where they can create the most value given their particular skills, interests, and company context.

For me, that’s meant writing a lot of code. It works because of my particular context: I enjoy building software more than org design, I have deep customer and codebase knowledge that makes me particularly effective, and we’ve hired strong engineering managers.

But this is my particular path, not a prescription. The CTO role is remarkably flexible. Whether building orgs, or developing product strategy, or something else — technical leadership varies depending on your strengths, what energizes you, and what your company needs.

If you’re an engineer worried that leadership means abandoning technical work, know that there are many paths. The key is figuring out where you’re uniquely great.
```

### external-why-i-code-as-a-cto--sentence-001

`train` - `approved` - 31 approximate tokens - 18 words

Headings: (intro or continuation)

```markdown
The job has shifted from “writing every line of code” to “providing context, making decisions, and evaluating solutions.”
```

## Five opinions on building things well

### five-opinions-on-building-things-well--001

`train` - `candidate` - 613 approximate tokens - 416 words

Headings: Stay somewhere long enough to see legacy code / Creativity should go to the right place

```markdown
I sometimes cringe at sharing my opinions (who cares about my opinions anyways), but I keep these around because back in college a similar "Opinions" section actually started some awesome conversations, so maybe it will in the future too. (These previously lived on a standalone page of this site — the first four date to October 2023, and the last was added in November 2025.)

# Stay somewhere long enough to see legacy code

Most engineers change jobs frequently, but the best engineers I've known tend to stay somewhere for a long time. It can be difficult seeing your peers move to exciting, flashy companies with big salaries and titles, but I've found that staying in one place gives you deep wisdom and perspective.

The caveat here is that you need to find a good company (somewhere that is growing and where you trust the leadership team). If you're able to find that, then:

- You'll learn how your decisions turned out. One of the key parts to learning is having a feedback cycle. If you don't stay at a company long enough, you'll never be able to see how the software you built turns out (whether good or bad).
- You'll constantly evolve yourself as the company changes. You'll tend to be provided opportunities as a company grows that you might not have gotten if you were a new hire somewhere else.
- You'll gain confidence in making things happen. As you spend time building in your current environment, you'll get better at it and start to understand what it takes to ship a product or feature.

# Creativity should go to the right place

If you look at any of the tables that are still around from hundreds of years ago, you'll notice they're typically made the same way: mortise and tenon construction. Mortise and tenon joinery is simple and straightforward, but also strong and long-lasting. It's been the gold standard for table construction for thousands of years.

The interesting thing is that while the construction method is typically the same, the style of antique furniture can be wildly different: from extremely ornate federal style furniture with marquetry and inlays of the 1700s to large, craftsman style pieces from the early 1900s.

Likewise, I believe the key to building timeless software is to build the bones of your system in a standard way, and to use your creativity in other areas. This means sticking with battle tested tooling (e.g. PostgreSQL) and innovating on solving user problems with your product.
```

### five-opinions-on-building-things-well--002

`train` - `candidate` - 569 approximate tokens - 375 words

Headings: It's not "Speed vs. Quality", it's "Speed + Quality"

```markdown
# It's not "Speed vs. Quality", it's "Speed + Quality"

I think the biggest determinant of quality is the skill of the craftsperson, not the amount of time someone spends focusing on quality. On the margins, it's true that if you spend more time on something, the output will tend to be higher quality.
But I also think a skilled craftsperson tasked with creating a table is going to take far less time and produce a higher quality product than an unskilled craftsperson who is focusing extensively on the quality of the outcome.

In my belief, skill and expertise are such overriding determinants of final build quality that I think we should talk about the "Speed + Quality" combination, i.e. becoming more skillful so that you can finish things faster AND with higher quality.

Here's an example: [Frank Strazza](http://www.strazzafurniture.com/), a well-known master woodworker, put on a dovetail demonstration at the [Texas Woodworking Festival](https://texaswoodworkingfestival.com/) where he finished a set of half-blind dovetails in 15 minutes. The end result was far more pristine and high quality than something that would've taken an amateur woodworker over an hour to finish.

You'll notice this in all disciplines: speed and quality are inherently linked. If you're an amateur, you likely don't have the ability to create something high quality yet. As you become more experienced, your work becomes higher quality because of your methods, tools, and general knowledge. It becomes easier and faster for you to complete work. At the same time, your minimum quality bar also increases and the work you output by default is higher quality.

Software engineering is no different. Take a look at Russ Cox's [PDF parsing library](https://github.com/rsc/pdf). He wrote this over a few weekends because he needed to parse some PDFs. The resulting library is still in use in many codebases (including Assembled's) and is considered one of the main libraries for parsing PDFs in Golang.

All this is to say: build lots of stuff and continuously improve as you build. The more pieces of furniture you create, the more software you write, the better the overall quality of your output will be so long as you're looking for feedback and constantly improving your techniques.
```

### five-opinions-on-building-things-well--003

`train` - `candidate` - 379 approximate tokens - 268 words

Headings: Beta fast, launch slow / If no one is ever mad at you, you're probably a bit too risk averse

```markdown
# Beta fast, launch slow

At [Stripe](https://www.stripe.com), there was a mantra that for new features, we should bring on beta users at 25% and launch at 98%. The idea was to focus early on product and idea validation, ensuring that you're iterating as soon as possible with real users. This was paired with extremely high standards for a feature launch -- we only fully launched the product to the public once all the kinks had been removed.

We use the same "Beta fast, launch slow" framework at Assembled to build high quality products that people actually want to use.

# If no one is ever mad at you, you're probably a bit too risk averse

If you’re trying to do anything meaningful, someone is going to be annoyed, uncomfortable, or outright mad at you sooner or later. If literally no one is ever upset with you, it might be a sign that you’re avoiding hard conversations, difficult tradeoffs, or ambitious bets.

When someone is mad, I’ve found it useful to pause and ask a couple of questions:

- Are they mad at a specific action I took (something I did carelessly, unfairly, or without enough context)?
- Or are they mad at what I represent (a change in direction, a standard I’m trying to uphold, a decision that breaks with the status quo)?

If they’re mad at my actions, there’s usually something I should fix, apologize for, or do better next time. If they’re mad at what I represent, there’s often at least a kernel of truth in the reaction, but it doesn’t automatically mean I should back down.
```

## How Claude's watermarking (probably) works

### how-claude-watermarking-probably-works--001

`dev` - `candidate` - 414 approximate tokens - 228 words

Headings: (intro or continuation)

```markdown
**Update (2026-08-20):** Anthropic has [since published technical details](https://www.anthropic.com/news/claude-text-watermark) confirming that Claude's watermark is based on SynthID-Text — a keyed statistical watermark on token selection, exactly as this post hypothesized. See the [update section](#update-2026-08-20-anthropic-confirms-its-synthid-text) near the end of the post for a full rundown.

---

Yesterday, [Anthropic announced](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content) that they had started watermarking AI-generated content. Folks across the internet were particularly up in arms about it (I think rightfully so), especially because this apparently is happening to all Claude models whether or not you are in the EU. I wanted to investigate what they're actually doing and whether it's perceptible or changeable.

Anthropic provides some insight into their approach in their article [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content). Though it doesn't actually provide any technical details on the implementation, it provides some guidance to help draw a wide net around the scheme they're using. The key clues Anthropic left in their help center article:

- The scheme "weaves an imperceptible watermark directly into the text itself. You won’t see it, and it doesn’t change the meaning, quality, or readability of Claude’s response."
- The watermarking doesn't work well on very short text.
- The watermark seems to have started recently (August 2nd or later)

This helps us narrow down the possibilities quite a bit.
```

### how-claude-watermarking-probably-works--002

`dev` - `candidate` - 479 approximate tokens - 302 words

Headings: Setup / No hidden unicode or whitespace

```markdown
# Setup

To actually get to the bottom of what Anthropic are doing, I realized that there are some interesting experiments you can run. [Gloaguen et al.](https://www.sri.inf.ethz.ch/blog/probingsynthid) created specific tests to check for statistical watermarking, and we can also perform an analysis of Claude outputs to check for things like hidden unicode or whitespace results.

For good measure, I also downloaded a dump of my Claude chats (I've used Claude Code since 2/4/2025 and have recorded 1206 sessions) and did a quick comparison to see if there was any changepoint around early August that percepitbly changed the mix of tokens that Fable 5 output (my usual daily driver model). I wasn't able to find any perceptible difference in this historical analysis, which confirms Anthropic's claim that the watermarking is generally imperceptible unless using more specific tests.

# No hidden unicode or whitespace

The second thing I checked is whether there's hidden unicode or whitespace or punctuation patterns. This was pretty conclusive: they're not doing something so simple.

An analysis across 7.2 million extracted prose characters (both on historical Claude Code text as well as generated Claude Code text on August 11) showed that the only unicode characters that were output by Claude were reasonable and part of day to day usage:

- Curly quotation marks, apostrophes, and horizontal ellipses
- Em/en dashes (A LOT of them unfortunately)
- Mathematical symbols
- Accented or non-English characters
- Emoji

An audit by Codex, with me spot checking about 10 samples, found no anomalous instances that were consistent with a hidden Unicode watermark. I similarly found no whitespace encoding marks.

This evidence, combined with the fact that the watermarking is imperceptible and doesn't work on short text, means that Anthropic is most likely using some form of statistical token watermarking.
```

### how-claude-watermarking-probably-works--003

`dev` - `candidate` - 609 approximate tokens - 414 words

Headings: Statistical watermarking schemes / Green/red lists

```markdown
# Statistical watermarking schemes

There are a few different schemes that are available that can add watermarking to text. I'll talk about the simplest version, the green/red list created in 2023 by [Kirchenbauer et al.](https://arxiv.org/pdf/2301.10226), because it's the easiest to explain and once you understand it will allow you to understand how these schemes generally work.

## Green/red lists

This scheme is super basic, but it's quite clever and fun. Here are the steps:

1. Split your output vocabulary into two sets: a green and a red list. Make sure they're chosen uniformly at random.
2. Then for the green list, add $\delta$ to all of the logits and sample from the updated distribution at decoding time.

To figure out whether a text has been watermarked, then you compute the z-score that the tokens in the green set appear. If the text wasn't watermarked, then the expected value of text in the green list is $T/2$, where $T$ is the token count, with a standard deviation of $\frac{\sqrt{T}}{2}$. So the suspiciousness of getting this outcome is just the z-score:

$$
z = \frac{2G-T}{\sqrt{T}}.
$$

If some red token already has probability 0.99 (which would be a huge logit lead) a big $\delta$ nudge to the greens still wouldn't overtake it. So the bias only changes words that have a lot of options and generally high entropy.

For an example, let's say you asked your LLM to write a poem, you might have the following potential sentences that get generated:

Word | List | Sentence
-----|------|---------
crisp | Green | It was a crisp morning
quiet | Green | It was a quiet morning
foggy | Red | It was a foggy morning
cold | Red | It was a cold morning

If it was watermarked, you'd get an imperceptibly higher percentage of generating "crisp" or "quiet" morning (depending on how strongly the LLM provider decided to watermark with their $\delta$ value). Do this across all the words that an LLM is generating, and you can get high levels of confidence in your watermarking.

That being said, I don't believe Green/red lists are used in practice because they're easy to detect and there are schemes that use the model's available entropy more efficiently (and thus harder to detect and less likely to change the outputs of the model). The most well known scheme is [SynthID-Text](https://www.nature.com/articles/s41586-024-08025-4) which was developed by Google Deepmind and is used by Google in production.
```

### how-claude-watermarking-probably-works--004

`dev` - `candidate` - 621 approximate tokens - 410 words

Headings: SynthID-Text

```markdown
## SynthID-Text

SynthID-Text is the same idea as green/red lists, but using a slightly different approach that Deepmind calls tournament sampling. Here are the steps:

1. At each decoding step, hash a secret key together with the last $h$ tokens of context to produce a seed. That seed assigns every vocabulary token one $g$ value in $[0,1]$ per tournament layer.
2. Draw your candidate output tokens using the model's logits as normal.
3. Run a tournament bracket where candidates face off in pairs, and the candidate with the higher $g$ value for that layer advances.
4. Output the tournament winner as the decoded token.

To detect the watermark, you just need the secret key. You can compute the seed value and the $g$ values associated with every token in the text:

$$
\operatorname{Score}(x)=\frac{1}{mT}\sum_{t=1}^{T}\sum_{\ell=1}^{m}g_\ell(x_t,r_t),
$$

Then compare the result with the null distribution and generate a standardized score similar to the Green/red list detection.

SynthID also uses repeated-context masking: if the same $h$-token context window has already been used during a response, the implementation can decline to watermark that position. This prevents a repeated context from receiving the same bias over and over, but it matters substantially for testing because using the wrong context length can accidentally trigger the mask and hide the signal.

SynthID is a bit more disguised than Green/red lists because every candidate is drawn from the model's own distribution, so the tournament can only promote words the model already considered saying. When the model is pretty certain about the next token, there's low entropy and not much watermarking (just like Green/red lists). The signal gets stronger for high entropy words, which is also why these schemes need a decent amount of text before detection becomes reliable.

When the model is nearly certain about the next token, there is little entropy available for any sampling-based watermark to use. The signal accumulates mainly at higher-entropy positions, which is one reason these schemes need a decent amount of text before detection becomes reliable.

Going back to our poem, say the model draws four candidates and we run a two-layer tournament using the continuous-score variant:

Matchup | g-values | Winner
--------|----------|-------
crisp vs. foggy (layer 1) | 0.71 vs. 0.24 | crisp
quiet vs. cold (layer 1) | 0.90 vs. 0.42 | quiet
crisp vs. quiet (layer 2) | 0.35 vs. 0.83 | quiet
```

### how-claude-watermarking-probably-works--005

`dev` - `candidate` - 497 approximate tokens - 324 words

Headings: Experimental results / Green/red list detection

````markdown
So "quiet" gets emitted because of its tournament $g$ values. It's clever because any single word looks like a standard part of the output, but with the secret key you can test whether emitted words repeatedly align with the keyed scores. It's also quite nice because you can adjust the number of layers to change the tradeoff between detectability and model quality.

SynthID is the only scheme that I know of (or ChatGPT/Claude knows of) which is running in production, and it seems like my best guess candidate given that it's been publicized and run a scale by Google.

# Experimental results

To see if Anthropic is running one of these kinds of statistical watermarks, I ran some of the black-box tests from the watermark detection literature with Codex GPT-5.6-sol[0].

## Green/red list detection

I had Codex run [Gloaguen et al.'s](https://www.sri.inf.ethz.ch/blog/probingsynthid) detection algorithm. In this, Claude is forced to complete sentences using one of four fruits:

```
I ate 111111111111111 peaches
I chose 222222222222222 plums
...
```

The prefix and repeated digit vary while the fruit alternatives remain fixed. If a classic keyed watermark partitions tokens into green and red sets, then a particular fruit should become unusually likely or unlikely.

Model/test | Number of runs | Permutation p-value
-----------|----------------|--------------------
Sonnet 5, compact digits | 1,800 | 0.677
Sonnet 5, spaced digits | 1,800 | 0.556
Fable 5 | 1,200 | 0.886


The Sonnet tests used 10 prefixes, 9 digit contexts, and 20 calls for each combination, for 1,800 responses each. The Fable test used 6 digit contexts, for 1,200 responses. Each p-value was calculated from 100,000 permutations.

All three were clear negative results. The Sonnet test was strong enough to rule out a fairly large, stable Green/red effect in this particular setup. It does not rule out a weaker watermark, a key that changes between requests, or a different kind of watermark entirely.
````

### how-claude-watermarking-probably-works--006

`dev` - `candidate` - 671 approximate tokens - 465 words

Headings: SynthID detection

````markdown
## SynthID detection

The next experiment looked for the fixed context window used by SynthID-like schemes. The basic setup forced Claude to return a line such as

```
I ate red green cherries
```

Here `red` is a perturbation word and `green` is repeated $H$ times after it. If the watermark only looks at the last $h$ tokens, `red` should stop affecting the watermark once $H$ reaches $h$. For example, if $h=2$, I would expect a strong effect at $H=1$ and little or no effect at $H=2$. So the thing we're looking for is a sharp drop at some value of $H$.

Here's an actual example of the experiment I ran:

| $H$ | Repeat | Actual response |
|---:|---:|---|
| 1 | 0 | `I ate red green cherries` |
| 1 | 1 | `I ate red green cherries` |
| 1 | 2 | `I ate red green cherries` |
| 2 | 0 | `I ate red green green plums` |
| 2 | 1 | `I ate red green green cherries` |
| 2 | 2 | `I ate red green green cherries` |
| 3 | 0 | `I ate red green green green cherries` |
| 3 | 1 | `I ate red green green green cherries` |
| 3 | 2 | `I ate red green green green plums` |

At larger scale, I calculated $Z(H)$, which measures how strongly changing the perturbation word changes Claude's fruit choice. A value near zero would mean no detectable effect. $Z(1)=87.25$, which I saw in the experimental runs, means the test statistic was 87.25 (!!) standard deviations above what you would expect to see in randomized data:

| $H$ | Context form | Standardized perturbation effect $Z(H)$ |
|---:|---|---:|
| 1 | `red green` | 87.25 |
| 2 | `red green green` | 58.42 |
| 3 | `red green green green` | 33.64 |
| 4 | `red` + 4×`green` | 37.22 |
| 5 | `red` + 5×`green` | 38.46 |
| 6 | `red` + 6×`green` | 25.34 |
| 7 | `red` + 7×`green` | 19.28 |
| 8 | `red` + 8×`green` | 25.10 |

That is an extremely strong result, with $H=1$ giving $p\approx0.00001$. Unfortunately, this test wasn't conclusive because it only tells us that the perturbation word matters, and we didn't actually see a sharp drop off on any $H$, only a slow decrease, which could mean that this isn't a watermark at all, but rather just an effect that comes from the model.

The full scan used 20,736 Sonnet 5 responses, with 2,592 at each value of $H$. The sharpest bend was at $H=2$, so I tested it again using fresh Sonnet 5 responses and also on Sonnet 4.6 (which based on my reading of Anthropic's help center article is less likely to be watermarked because it's an older model):

| Endpoint | Observations | $Z(1)$ | $Z(2)$ | $Z(3)$ | $D(2)$ |
|---|---:|---:|---:|---:|---:|
| Sonnet 5, held-out confirmation | 7,776 | 85.77 | 61.90 | 33.35 | 38.14 |
| Sonnet 4.6, matched comparison | 7,776 | 105.49 | 70.61 | 76.25 | 32.06 |
````

### how-claude-watermarking-probably-works--007

`dev` - `candidate` - 466 approximate tokens - 323 words

Headings: Conclusions

```markdown
The bend appeared again in the fresh Sonnet 5 data. But the effect did not disappear at $H=2$: the $Z(2)$ and $Z(3)$ values were still enormous. Sonnet 4.6 also showed a very similar bend.

This makes the result much less exciting than the huge numbers initially suggest. Sonnet 4.6 might also be watermarked, so it is not a true negative control, but it does seem the pattern is not unique to Sonnet 5 and does not look like a clean context-window boundary. The most likely explanation is that words like `red` and `green` naturally change how Claude chooses among fruits.

So this was a strong detection of a prompt effect, but not a positive detection of SynthID. It also doesn't rule out a different watermark that this test cannot see.

# Conclusions

My current best guess is that Anthropic is using a private-key watermark that changes token selection as Claude generates text. But that guess comes mostly from Anthropic’s description and negative results in other tests as opposed to a positive result in my experiments.

I was able to rule out a few things as I found no evidence of hidden Unicode or whitespace, and the constrained-choice tests argue against a large, stable Green/red bias. That said, the apparent SynthID signal turned out to be a likely strong prompt effect that also appeared in Sonnet 4.6, so it doesn't necessarily positively identify a watermark.

Note that I'm not actually sure whether the watermarking rollout is fully complete yet and which models it's available on. From Anthropic's own help center article, it says that models are going to be watermarked going forward and that support for any existing model is "in progress". I think I'll have to re-run this analysis again in a few weeks or when there's a verifiable model that does have watermarking enabled and is confirmed by Anthropic. We'll just have to wait and see.
```

### how-claude-watermarking-probably-works--008

`dev` - `candidate` - 603 approximate tokens - 367 words

Headings: UPDATE (2026-08-20): Anthropic confirms it's SynthID-Text

```markdown
# UPDATE (2026-08-20): Anthropic confirms it's SynthID-Text

Well, we didn't have to wait very long. Two days after I published this post, Anthropic put out a [blog post](https://www.anthropic.com/news/claude-text-watermark) with actual technical details (covered by [TechCrunch](https://techcrunch.com/2026/08/15/anthropic-shares-more-details-about-how-claudes-new-watermarks-will-work/) among others). Anthropic notes that Claude's watermark is based on SynthID-Text, just as was predicted by this post. It's nice to get one right occasionally!

Going through what Anthropic confirmed point by point:

- **It's a keyed statistical watermark on token selection.** In Anthropic's words: "Instead of using an arbitrary random number generator to pick the next word, watermarking uses the key and a few words that come before to settle what word the model should pick." That's the same mechanism from the SynthID-Text section above.
- **No hidden characters.** Straight from Anthropic: "Nothing is added to the text and there are no hidden characters." This matches the Unicode and whitespace analysis above (where my analysis of 7.2 million characters turned up nothing)
- **Paraphrasing defeats it.** Light editing preserves the watermark, but larger rewrites where a large number of words are adjusted will remove the watermark. This is consistent with my note above that a paraphraser sidesteps this watermarking fairly easily.
- **No performance cost.** No extra tokens, no added latency, and (per DeepMind's original Nature results) no statistically significant quality difference.
- **A detection API is coming.** This one is a fun piece of new information. Anthropic says they will "soon be offering a watermark detection API," with details still being worked out. They also state the watermark can't be traced back to a specific person, organization, or chat. I'd bet that you'll be able to pass text to their API, they'll run an analysis using the secret key, and then they'll give you the confidence / probability they have that it was indeed watermarked by Claude.

I also went ahead and re-ran the completed Sonnet 5 experiments on August 20, collecting 11,676 fresh responses with the same prompts and analysis as the August 11–12 archive. The short version is that Sonnet 5's behavior changed substantially between the two runs, but the results did not necessarily change the original analysis much:
```

### how-claude-watermarking-probably-works--009

`dev` - `candidate` - 348 approximate tokens - 214 words

Headings: (intro or continuation)

```markdown
| Probe | Archived result | August 20 re-run | Reading |
|---|---:|---:|---|
| Compact-digit red/green | p = 0.6769 | p = 0.2204 | Negative in both runs |
| Space-separated red/green | p = 0.5558 | p = 1.0000 | Negative in both runs |
| Fixed sampling | 300/300 unique | 300/300 unique | No collisions in either run |
| Context shielding, Z(H=1/2/3) | 85.77 / 61.90 / 33.35 | 84.25 / 59.46 / 32.73 | Basically the same shape as the original experiments |

There was nevertheless very strong drift from early August. Only 65.17% of the compact-digit choices, 58.44% of the spaced-digit choices, and 80.94% of the context-shielding choices exactly matched their archived counterparts. Paired randomization tests were at the Monte Carlo floor (p = 1/100001) for all three datasets. Reported median output-token counts also moved from, which would suggest that token accounting or effective tokenization changed as well.

So something in Sonnet 5's serving, sampling, tokenization, or surrounding configuration definitely changed. What did *not* appear was a new watermarking signature that lets me attribute that movement to SynthID-Text. Anthropic says support for pre-August 2 models will be added over the coming months, and it has not published a known-positive backport date for Sonnet 5. A confirmed watermarked endpoint or the promised detection API is still needed to close that loop.
```

### how-claude-watermarking-probably-works--010

`dev` - `candidate` - 473 approximate tokens - 332 words

Headings: A note on the future of watermarking / Footnotes

```markdown
# A note on the future of watermarking

While this is mostly a technical post, I do think it's worth thinking about what this potentially means for the future. It's already relatively easy to detect when AI was used to write something and someone was careless. For example, I don't need a statistical measure to figure out that this was written by an LLM: "That's not a documentation problem — it's a retrieval problem."

In my view, putting statistical watermarks like the one described in this post on all LLM output greatly ratchets up the stakes from what is easily perceptible by humans, and in a way that is particularly undemocratic. You'll only be able to detect the watermark if you're in a select group that has access to a secret key (e.g. frontier lab employees or government / police). While this particular change is somewhat innocuous in my opinion, as I would assume most content written in the years after 2026 will be LLM generated or at least LLM assisted, it is a bit scary to know that a single relatively undemocratic, but innocuous change can give way to many more that may not be as innocuous. The EU transparency code that Anthropic is following has basically mandated that watermarking of text is required from model providers operating in the EU, so unfortunately, we should expect this to happen to a lot more of our model output.

Thankfully, sidestepping this kid of watermarking is fairly easy with a paraphraser or rephraser that doesn't have a watermark (or just rewriting the text by hand). The watermarking is more meant to raise the cost and annoyance of doing so.

# Footnotes

[0] Of course, I tried to use Fable 5 for the analysis to start with, but it failed the security classifier and fell back to Opus 5 and I had to rely on the old trusty GPT-5.6-sol. This was probably better anyways as I'm not sure Claude would want itself to be self inspected.
```

## Learnings from the Codex repo

### learnings-from-the-codex-repo--001

`test` - `candidate` - 458 approximate tokens - 341 words

Headings: (intro or continuation)

```markdown
I've been fascinated recently at what the best practices in the new age of engineering look like. But it's hard to find real data on best practices. For example, X has a ton of "information" about what's happening at the cutting edge, but it's very hard to validate whether any of it is real. Talks suffer from the same problem as an exec at a company can say anything they want or stretch the truth. Are people really not looking at any of their code? Are people productively using billions of tokens every day? It's hard to get ground truth on that.

Because of that, I thought OpenAI's open source [Codex repo](https://github.com/openai/codex) would be an good place to get a bit closer to ground truth:

- OpenAI's internal teams have access to edge of the frontier (it's rumored that Astra is a step change above GPT-5.6-sol for example)
- The Codex repo has been open source since it was launched in 2025, so there's plenty of stuff that has happened in the open.
- OpenAI likely has the best pulse of any company in the world (save a few) on how to build software in the agentic engineering way

So I kicked off an analysis of the repo using a combination of Codex (gpt-5.6-sol) and Claude Code (Fable 5) to try to see what they were doing.

My immediate observation is that Codex has seen a step change increase in PRs per week over the last few months. In May 2025, the Rust implementation had 98 commits from six authors, and one person wrote 89 of them. In the first 25 days of August 2026, it had more than 1,000 commits from 135 authors. This is a big jump, and it's an interesting convergence of a few factors: a) likely a lot of coding agent usage b) aggressive hiring for the team and c) heavy investments in guardrails and automation rules that make it easier for many people and agents to work at the same time.
```

### learnings-from-the-codex-repo--002

`test` - `candidate` - 457 approximate tokens - 289 words

Headings: Graduating from small team / handwritten-ish code to large team with agents

```markdown
# Graduating from small team / handwritten-ish code to large team with agents

The [public Codex repository](https://github.com/openai/codex) started on April 16, 2025 as a TypeScript CLI. Since then, the repo has changed quite significantly. The initial era of the Codex repo had a small number of authors pushing out everything. For example, Michael Bolin [wrote the original Rust implementation](https://github.com/openai/codex/commit/31d0d7a3059063ef266cab1644aa82f87a866c19) and also 150 of the first 169 Rust commits.

However, over time, this has changed dramatically:

|  | May 2025 | March 2026 | August 2026 |
|---|---:|---:|---:|
| Commits per month | 98 | 791 | 893 |
| Regular author identities with 5+ commits | 2 | 28 | 35 |
| Share written by the busiest author | 91% | 14% | 18% |
| Authors landing changes on the median active day | 1 | 12 | ~18 |
| Rust crates touched on the median active day | 4 | 16 | ~28 |

The volume of changes grew roughly 8x, from 98 commits in May 2025 to 791 in March 2026. By August, the repository was already hitting 900 commits. Commit counts are an imperfect measure of output, especially as development practices change, but the surrounding evidence points to a similar story -- there were more authors were shipping on the same day, across many more parts of the codebase.

Even though coding agents have recently gotten much better, part of the sizeable increase in Codex velocity comes down to sheer team size. OpenAI appears to have put a lot more people on the project (137 members now) and generally been able to keep people working on separate parallel streams of work (most authors seem to be working on separate, parallel crates).

With that many more people and agents changing the code at the same time, the rules around how they work become much more important.
```

### learnings-from-the-codex-repo--003

`test` - `candidate` - 645 approximate tokens - 391 words

Headings: Agent guardrails and rules

```markdown
# Agent guardrails and rules

The first interesting thing is the repo's [`AGENTS.md`](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md) file. The Codex repo takes this fairly seriously: it's clear they've put a lot of thought into and have been aggressive at removing slop and extras (the main file is 322 lines).

There are five rules in particular that I found interesting:

**1. "Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`."** [Some tests check these variables](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/suite/compact_resume_fork.rs#L18-L60) to figure out whether they can safely run nested sandboxing or network behavior. An agent might otherwise see those checks, decide they are getting in the way of a test, and "fix" them. I think it's quite smart to find these types of cheating behaviors that you've seen in test runs and encode them as rules.

**2. "Do not add tests for values that are statically defined" and "Do not add negative tests for logic that was removed."** These rules are aimed at tests that make a change look more rigorous without checking any meaningful behavior. Coding agents are very good at generating this kind of plausible-looking test volume, so explicitly telling them what not to test keeps the suite focused on behavior that can actually regress.

**4. "Features that change the agent logic MUST add an integration test."** Agent behavior usually comes from the combination of context, tools, model responses, and the turn loop, so a small unit test often can't tell you whether the agent will actually do the right thing. Codex's [`TestCodexBuilder` test harness](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/common/test_codex.rs#L325-L341) runs the real agent loop against fake model streams. New tests are also supposed to use [an automatic environment setup](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/common/test_codex.rs#L485-L499) so they keep working when the app-server and exec-server are on different operating systems.

**5. "Avoid bool or ambiguous `Option` parameters."** If an API can't be changed, opaque values like `false`, `None`, or a bare number need an exact `/*param_name*/` comment next to them. This is already more specific than what you normally see in an instruction file, but the interesting part is that they didn't leave it as an instruction.
```

### learnings-from-the-codex-repo--004

`test` - `candidate` - 479 approximate tokens - 320 words

Headings: Lint rules

````markdown
# Lint rules

The ambiguous argument rule is probably my favorite example of what the team does next. Rust makes it easy to end up with calls like this:

```rust
foo(false, None, 1000)
```

It is basically impossible to review that without jumping to the function definition. The Codex team would prefer that you change the API, but when that is impractical they require comments next to ambiguous literal arguments:

```rust
foo(
    /*enabled*/ false,
    /*parent_turn_id*/ None,
    /*timeout_ms*/ 1000,
)
```

They then built a [custom lint](https://github.com/openai/codex/commit/4b31848f5bd112816eb0f7f4e9a33dc2330ea617) that checks whether the comment exactly matches the parameter name in the function definition. It was introduced in March 2026, applied across the Rust workspace a couple of days later, and then moved into Bazel CI.

The other thing worth saying is that these rules did not appear all at once. Support for `AGENTS.md` landed in May 2025. More detailed test guidance followed that summer. Snapshot requirements came in February 2026, the warning about `codex-core` in March, the trait guidance in April, and the model context and change-size rules in June. It looks a lot like the team is taking repeated review feedback and putting it somewhere that the next person or agent will see before making the same mistake.

You can see a rough pattern here: a problem first shows up repeatedly in code review, it gets written into `AGENTS.md` so humans and agents see it before making a change, and then the team turns it into a lint or CI check once the rule is stable enough. Not every rule makes it to the last step, but the expensive and objectively checkable ones tend to.

Codex has 38 lint rules, and I think it's part of what makes the repo easier to work on as an agent because it has a large number of automated checks that prevent out-of policy behavior (and in a deterministic way).
````

### learnings-from-the-codex-repo--005

`test` - `candidate` - 585 approximate tokens - 391 words

Headings: Investing in an integration test harness

```markdown
# Investing in an integration test harness

One other thing that I thought was interesting was how much the Codex team has invested in their tests. Tests compose about 615k lines (or 40%) of the codebase, and Codex has also invested in a full mock test harness: they've spent around 7k lines of code across 300+ commits to built out a harness that can stub out http responses from the Responses API. This integration test harness will run a real Codex thread, and it can call tools, apply approvals, and generally iterate on requests as if it's getting responses back from the LLM. It's a really interesting and deterministic way to test a large amount of behavior, and I think it's quite smart to have invested so heavily in this because the Codex loop is ultimately the most important part of the product.

Another area that I was curious about (especially because our team has seen our test suites slow down as our coding agents get better and faster at writing tests), is how they're still able to keep up speed of development despite a large number of tests. Codex doesn't run the same enormous test suite at every stage. While someone is working on a change, the setup is to test only the affected Rust crate. If you change the terminal UI, for example, you run the terminal UI tests, not the entire workspace. This keeps the everyday edit-test loop reasonably fast.

Before a change is merged, CI broadens the coverage. Bazel runs the compatible Rust tests across macOS, Linux, and Windows, while separate jobs check the SDKs, formatting, dependencies, and repository rules. The largest workloads are divided across machines and reuse remote build caches.

After the code reaches main, Codex pays for a much more exhaustive pass. It runs the full Cargo test suite across five platform and architecture combinations. Each platform compiles the tests once, packages the resulting binaries, and distributes their execution across four machines. Slower native Windows checks, release builds, and remote-environment tests also happen here.

Basically, Codex has set up their environment so only relevant tests are run while developing, and get progressively more thorough as a piece of code gets closer to deployment. This makes it so you can still have fast deploys and ship quickly, while keeping safety and correctness in the long run.
```

### learnings-from-the-codex-repo--006

`test` - `candidate` - 400 approximate tokens - 235 words

Headings: Migrations with linting and feature flags

```markdown
# Migrations with linting and feature flags

The other fascinating thing we observed in Codex's codebase is some good old-fashioned, high-quality engineering. Their engineering team uses a combination of feature flags, linters, and other rollout mechanisms to ensure safety but also speedin rollout. Large changes are staged so the old and new implementations can coexist, and the migration plan is eventually encoded in lint rules instead of depending on everyone remembering it.

The TUI migration is a nice example. On March 16, the team created a [temporary parallel implementation](https://github.com/openai/codex/commit/db89b73a9cd553ac2a2afda93c9f9bdcc223540c) behind a `tui_app_server` feature flag. Ten days later, they [enabled it by default](https://github.com/openai/codex/commit/e7139e14a29de0411a61658a0e5765e2502a0cd2). Once it was stable, they [deleted the old TUI and retired the feature flag](https://github.com/openai/codex/commit/d65deec61718f291cba5a51de9489603865779df), while continuing to accept the old flag in configuration so existing users would not get an error.

Two weeks later, they added a [CI rule preventing the TUI from importing `codex-core` directly](https://github.com/openai/codex/commit/66e13efd9cfd0dd3525713c8cf27ea7fbcb6b3e4). I think this is a particularly good way to finish a migration. It's easy to clean up a dependency once, but on a team this large, someone will eventually add it back unless CI stops them. The feature flag made it easier to move over incrementally, and the lint rule made sure the team couldn't accidentally undo the work later.
```

### learnings-from-the-codex-repo--007

`test` - `candidate` - 270 approximate tokens - 175 words

Headings: Conclusion: speed == testing, boundaries, lint, hiring

```markdown
# Conclusion: speed == testing, boundaries, lint, hiring

The Codex team is running and building upon a highly used, production-level codebase while moving incredibly quickly. They've ramped up velocity considerably in the last few months through a combination of AI coding agent usage as well as hiring for new team members. There are a lot more people working on Codex than there were a year ago and many of those people appear to be very effective engineers. Also, the codebase is explicitly organized to give agents context. OpenAI have invested in the tests and boundaries that let all of those people and agents work at the same time.

The interesting thing is that at least for the Codex team, as implementation got cheaper, it did not make the rest of engineering less important. Codex put a lot of work into a well-designed system, particularly focused on the classic parts of engineering excellence: testing, high quality boundaries and abstractions, automatic linting systems, and of course hiring good people. All of those things seemed to have gotten more important.
```

## Mamba-3

### mamba-3--001

`train` - `candidate` - 689 approximate tokens - 463 words

Headings: (intro or continuation)

```markdown
Mamba-3 just dropped yesterday. It's a big milestone towards unseating the stranglehold that transformers have on the modern AI industry.

Mamba-3 is a state space model, and it's fascinating because it uses an entirely different architecture from transformers (the tech that the big LLMs like Opus 4.6, GPT 5.4, Gemini 3, etc. are based on).

Transformers keep a huge memory layer called the KV cache: this essentially stores all the memory of everything previously said in a conversation when it is computing the next token. It needs this because that ability to look at previous history is core to how it's able to reason well on large volumes of input data (this is called self-attention).

The downside of a transformer is that as you increase the number of inputs (the prefill phase where it's reading your system prompt) and outputs (the decoding phase where it's generating text), you're increasing the KV cache with each new token. This means by default that transformers are quadratic in their memory constraints, so large inputs slow these models down dramatically over time. Of course the big labs have figured out clever ways to improve performance here, but the math of the base transformer still slows down over time.

Modern state space models (like Mamba) use a very different approach: they keep a single fixed-size hidden state $h$ that adjusts over time: $h_t = A_t \, h_{t-1} + B_t \, x_t$ (where $A_t$ and $B_t$ are data-dependent matrices generated on the fly based on the current input vector $x_t$). This allows the model to selectively choose what to remember and what to forget.

There's a few magical things about state space models:

1. They're much more efficient over long context because computation grows linearly in size (instead of quadratically). This is perfect for audio because there's a huge amount of data in an audio file, much more than in text. This is one major reason why Cartesia is a leader in the audio space (their lab pioneered the modern state space models).

2. State space models can use linear algebra tricks to compute the prefill phase incredibly quickly. Notice that $h_1 = A_1 \, h_0 + B_1 \, x_1$ and $h_2 = A_2 \, h_1 + B_2 \, x_2$. This means that you can actually entirely skip the computation of the hidden state $h_1$ if you just use a bit of algebra:

    $$h_2 = A_2 \, A_1 \, h_0 + A_2 \, B_1 \, x_1 + B_2 \, x_2$$

    Previously, you would need to compute each token and feed that in as input into the next token, but with state space models, you can skip that and compute the last hidden state immediately. Then when you get to the decoding phase where you're actually doing inference on the new tokens, the state space models switch over to computing the hidden states one at a time.
```

### mamba-3--002

`train` - `candidate` - 523 approximate tokens - 348 words

Headings: (intro or continuation)

```markdown
Mamba-3 in particular does some really interesting stuff to make inference more efficient. I think the team has correctly recognized that there's a big shift happening in the world of AI: as coding models and LLMs more generally start to run larger and larger workloads, inference has started to become a bigger percentage of GPU usage. It used to be that labs would spend the majority of their GPU fleet on research and training, but now that AI is out in the wild and being used quite extensively, inference is much more important.

Mamba-3 has a few optimizations for this:

- **Multi-input, multi-output.** Previous generations of Mamba models would calculate the output tokens one at a time, similar to what most transformer-based architectures do. But the researchers noticed that GPUs are mostly bottlenecked on moving memory from VRAM to the compute cores. So, they restructured the math to group multiple state updates together into a big matrix multiplication, forcing the GPU to do more math at once while it waits.

- **Complex numbers for memory.** If you apply a real number multiple times, it can only go up or down. For example, if you multiply something by $0.9$ many times, that number will tend to zero. If you multiply by $1.1$ many times, that number will tend towards infinity. One problem of previous Mamba models was that if your memory only contains real numbers, you'll either definitely forget something or definitely remember something given sufficient time.

  Mamba-3 adds complex numbers to its memory, which can rotate in space. For example if you multiply $1$ by $i$ multiple times, you get back to $1$ after 4 multiplications: $1 \cdot i = i$, $\; i \cdot i = -1$, $\; {-1} \cdot i = -i$, $\; {-i} \cdot i = 1$.

  This means that Mamba-3 has the ability to track cycles, oscillatory patterns, etc.

It seems like the big labs are still mostly optimizing transformers, but hybrid models like AI21's Jamba and Google's Griffin already exist, and I bet that the next wave of models combining Mamba blocks and transformer blocks will be just around the corner.
```

### mamba-3--sentence-001

`train` - `approved` - 21 approximate tokens - 13 words

Headings: (intro or continuation)

```markdown
This means that Mamba-3 has the ability to track cycles, oscillatory patterns, etc.
```

## Time

### time--001

`train` - `candidate` - 144 approximate tokens - 104 words

Headings: (intro or continuation)

```markdown
I've been thinking about time lately, especially how much of it is available. The strange thing I keep coming back to is that life feels both incredibly long and incredibly short at the same time, depending on which angle you look at it from. Both things can be true at the same time. It reminds me of the coastline paradox: a coastline wraps around a perfectly finite patch of land, yet the closer you measure it, the longer its edge gets, running off toward infinity the finer your ruler. It's both finite and infinite at the same time, depending on how closely you look.
```

### time--002

`train` - `candidate` - 578 approximate tokens - 374 words

Headings: Life is long

```markdown
# Life is long

Life expectancy in the United States is relatively long compared to 100 years ago. You can expect to live 76 years for males, 81 for females, and even these statistics are skewed downwards because of COVID deaths and drug overdoses, so if you're a generally healthy person, you can expect to live [5-10 years longer than those baselines](https://www.cdc.gov/nchs/products/databriefs/db548.htm).

I've watched people have full-blown renaissances when they hit 40 or 50, and when you look closely it's almost never out of nowhere: it's compounding on a lifetime of work and learning that finally found its moment.

There's a long list of people who started their best-known company after 40: Eric Yuan (Zoom), Chip Wilson (Lululemon), Tony Fadell (Nest), Joseph Lubin (Ethereum). And in fact, most unicorn founders are actually in their [30s](https://www.patreon.com/TheVentureMindset/shop/unicorn-report-466660?source=storefront), and the average one has [14 years of industry experience](https://www.signalfire.com/blog/unicorn-founder-origins-data-report) before founding, up from 8 years in 2010. Experience and network seem to be key components of making something very important, things you can only get from age.

To me, it's exciting because there are many examples of compounding in practice. The most famous example is probably Nvidia: Jensen Huang had been running Nvidia for 30 years before the LLM revolution, and he had spent that time quietly amassing a team and company filled with expertise and focused execution. That compounding was really unleashed when the AI revolution occurred and he was able to put Nvidia in exactly the right spot to capitalize on it's expertise and moat.

OpenAI looks similar, though on a shorter timespan. I remember when OpenAI was most famous for OpenAI Five, an AI system that played [Dota 2](https://openai.com/index/openai-five-defeats-dota-2-world-champions/) and defeated world champions. It was a toy at the time with no practical application, just like what they could GPT-3 and GPT-3.5 would be. They were only focused on developing great AI models, and that allowed them to compound their research advantage.

My takeaway from this view is simple: keep learning and keep building. The runway is much longer than it feels in any given year.
```

### time--003

`train` - `candidate` - 699 approximate tokens - 503 words

Headings: Life is short / Enjoy it

```markdown
# Life is short

But the paradox is that even though life is long, our perception of time speeds up as we age. It's a [well-documented phenomenon](https://pubmed.ncbi.nlm.nih.gov/16512313/), usually attributed to two things a) the decreasing novelty of day-to-day life and b) the shrinking proportion of current time relative to everything you've already lived. A year is a tenth of a ten-year-old's life and a fortieth of a forty-year-old's, so of course it feels like it's flying by.

This means that if you're only halfway through your life expectancy by the calendar, you're actually much further than halfway through your perceived life. The clock and the felt experience are running at different speeds.

Time also compresses when you're heads down on something. Michael Siffre did [a famous experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC10115684/) where he lived in a cave cut off from sunlight and clocks for months, and he experienced enormous time compression: he thought only about 150 days had passed when it had actually been closer to 180, and at one point counting to what he believed was 120 seconds took him 5 minutes. You can see a gentler version of this when a child is lost in coloring or when you surface from deep focus and realize hours are gone.

Another reason why life is short is because the quality, health, and vigor you have at any given point of time declines. Your raw life force is generally strongest in your 20s and 30s. People in their 40s and 50s tell me constantly that they used to have way more energy. I didn't want to believe it, but then I remembered that in my 20s, the 30-year-olds kept telling me my body would hurt more and injuries would take longer to heal, and I didn't believe that either until it turned out to be completely true. On top of the energy curve, it generally gets harder to learn and grow into entirely new paths as you get older. Not impossible, just more effort than it took when you were younger. So you can have multiple things working against you at once.

I'm in my 30s now, and I still have an incredibly active mind with more ideas than I can act on. But I'm just more tired than I used to be. It's harder to stay up for long stretches, and a bad night of sleep hits me much harder than it once did. I suspect that only continues.

# Enjoy it

So life is both long and short, depending on the angle. Long enough that it's never too late to start, and that compounding will reward patience. Short enough that the years you have the most energy and the most novelty are finite, and they're quietly accelerating past.

For me, I'm focusing on working on building things / working on problems I genuinely enjoy and continuing to learn from incredible people. I just hope to stop to smell the flowers every now and then.
```

### time--sentence-001

`train` - `approved` - 11 approximate tokens - 9 words

Headings: (intro or continuation)

```markdown
Both things can be true at the same time.
```

## Number of tokens shouldn't be the only metric

### tokens-shouldnt-be-the-only-metric--001

`train` - `candidate` - 481 approximate tokens - 343 words

Headings: (intro or continuation)

```markdown
I've heard of a lot of teams recently starting to use number of tokens as the key metric by which they measure their engineering team.

It's actually kind of funny that I even feel the need to write this blog post, but I did want to get it on record: I think it's a bad metric if it's your primary north star.

Should it be one of many metrics that you use to understand how people on your team are performing? Yes. You definitely want some observability into how your engineers (or non-engineers) are using LLMs. But gamifying it and making it THE key metric is just a recipe for disaster.

As I'm sure some companies have found out by now, there are a number of reasons why this isn't a good idea:

- Tokens scale linearly with cost. While that may not be a problem early on, I guarantee you it will be a huge problem later on when you're paying out the nose to Anthropic and OpenAI but can't easily switch the volume off. Tokens tend to be reasonably sticky because it's not easy to change workflows, especially if you have automations running that require tokens. Often it's a project to go and identify where all the cost is coming from, categorize whether that cost is worthwhile, and then figure out how to stop it and possibly migrate systems off of LLMs.
- It's a fast-tracked way to create an organization of Slop Cannons. If you are literally incentivizing tokens, then the incentive is for people to spend them as quickly as possible. Even if they're not outright causing outages, low quality PRs being shipped into production can be slowly insidious over time. You're incentivizing usage over anything else. More generally, tokens don't tell you anything about whether the work was good. A 1M token agent run that fixes nothing looks identical on the dashboard to a 1M token agent run that ships a hard refactor. If your North Star metric can't distinguish those two, your metric is lacking in a key dimension.
```

### tokens-shouldnt-be-the-only-metric--002

`train` - `candidate` - 489 approximate tokens - 335 words

Headings: But I want people to use AI and to change their behavior! / So what should we actually look at?

```markdown
# But I want people to use AI and to change their behavior!

Great, I do too, but the lesson I keep learning is that you can't really skip the hard work that is required for behavior change.

I think you should be optimizing for the people who are really excited to use AI and really putting them in charge of moving the organization, and then creating a wave of excitement about what's possible now.

The handful of people on your team who are already curious will figure things out faster than any incentive program will. Pair them with engineers who haven't had their "aha" moment yet. Let them ship something visible. Run internal demos. Share war stories about workflows that went from hours to minutes. Behavior change happens through demonstrated value, not through KPIs denominated in tokens.

The other thing worth saying: if your team isn't using AI at the rate that you want, the problem is almost never that they need a quota. It's usually that the tooling is rough, the workflows aren't obvious, or nobody on the team has shown them what good looks like yet. None of those problems get solved by putting a token counter on the wall.

# So what should we actually look at?

If you want metrics, look at outputs rather than inputs. Some questions I'm asking our team:

* Are we shipping more product per engineer than we were six months ago?
* Are we resolving customer issues faster?
* Are people taking on projects they wouldn't have attempted before?
* When engineers describe their week, do they sound more energized or more drained?

Tokens are an input, and the metrics that matter are almost always outputs. Optimize an input and you'll get more of it, but you won't necessarily get the thing you actually wanted.

Should you watch token usage? Definitely! Use it for cost forecasting, for understanding adoption curves, for spotting people who might benefit from a nudge or some coaching. Just don't make it the only thing that matters.
```

### tokens-shouldnt-be-the-only-metric--sentence-001

`train` - `approved` - 19 approximate tokens - 13 words

Headings: (intro or continuation)

```markdown
Tokens are an input, and the metrics that matter are almost always outputs.
```

## Why are executives enamored with AI but ICs aren't?

### why-are-executives-enamored-with-ai-but-ics-arent--001

`train` - `candidate` - 166 approximate tokens - 104 words

Headings: (intro or continuation)

```markdown
I think there’s pretty clearly a divide in AI perception between executives and individual contributors (ICs). Executives seem to love it and evangelize it (going so far as to creating mandates at their companies for AI usage). But ICs are typically much more skeptical of its usage. You can see the divide show up everywhere from Hacker News comment threads to internal Slack debates about adopting coding agents.

Here's my current posit for why there's such a big divide: executives have always had to deal with non-determinism and focus on nondeterministic system design, while individual contributors are evaluated by their execution on deterministic tasks.
```

### why-are-executives-enamored-with-ai-but-ics-arent--002

`train` - `candidate` - 586 approximate tokens - 381 words

Headings: Managing non-deterministic systems

```markdown
# Managing non-deterministic systems

Executives have always had to deal with non-determinism. That’s par for the course:

- People being out sick or taking time off unexpectedly
- Someone not finishing an important project and not talking about it until far too late in the process
- People reacting to an announcement in an unexpected way
- A feature being built in a way that doesn't make sense with respect to the rest of the product, but does technically achieve objectives.

More generally, if you've ever taken a Chaos Theory class in math, you'll know that nonlinear, chaotic systems emerge when individual agents in a system are all acting with different inputs, utility functions, etc. Systems become slightly easier to manage if you're able to make those utility functions consistent (you're able to get a grasp on system dynamics).

A manager's job is to create a model of the world and align everyone's utility functions, knowing that there's a large amount of non-determinism in complex systems. So it makes sense that as a manager, you're ok with a decent amount of this.

AI is something that is non-deterministic but has a lot of characteristics of a well behaved chaotic system (specifically a system where you can understand the general behavior of the system, even if you cannot predict the specific outcomes at any point in time).

For example:

- LLMs generally continue their work and provide an output regardless of time of day, how difficult the task is, how much information is available
- LLM's deficiencies have well defined failure modes (e.g. hallucinations, lack of ability to operate outside of their context, and especially poor outcomes when not given enough context)
- The types of tasks that an LLM can accomplish are relatively well known, and the capability envelope is getting mapped out quickly. This is different than humans, where each person has a different set of strengths and weaknesses and where you need to uncover these over time.

Many of these properties are more deterministic than large human systems, which makes AI incredibly attractive for an executive who is already used to this and likely has put a large amount of effort into adding determinism into their systems already (e.g. by adding processes and structure in the form of levels and ladders, standard operating procedures, etc.).
```

### why-are-executives-enamored-with-ai-but-ics-arent--003

`train` - `candidate` - 647 approximate tokens - 431 words

Headings: ICs live in a more deterministic world

```markdown
# ICs live in a more deterministic world

ICs are generally much more focused on particular problems that have specific inputs and outcomes. Correctness is easier to determine, and how good you are at your job can largely be described by quality and speed, where the weights on those two depend on which organization you're in. This changes as you move up the ladder (a staff engineer is expected to tackle large, ambiguous business problems), but for most ICs, the world is relatively well defined.

ICs deal with plenty of non-determinism in practice (unclear requirements, flaky systems, shifting priorities), but the way they're evaluated pushes in the other direction. An IC's value often comes from being reliably precise (e.g. writing correct code, getting the analysis right, producing a design that holds up under scrutiny). The more deterministic your output, the better you are at your job.

AI introduces non-determinism into exactly this space, and from an IC's perspective, there are good reasons to be skeptical:

- **It's not as good as they are at their job.** A highly trained human focused on a specific task will often beat an LLM, especially if that task is long running, requires connecting multiple systems, or demands precise domain intuition. If you're an expert and you're handed a tool that does a mediocre version of your work, the overhead of fixing its mistakes can genuinely cost more than doing it yourself.
- **It changes what their job is.** You go from doing the work yourself to managing something that does the work. The skills that got you hired (deep focus, precision, domain knowledge) aren't necessarily the skills that make you good at that. That's a disorienting shift.
- **It's tied to self worth.** Work accounts for the majority of a person's waking hours. When executives talk about AI making everyone more productive, ICs can hear that as the things you've spent years getting good at are about to matter less. Whether or not that's what's actually being said, it's a reasonable thing to feel.

One note: organizations that bias towards speed over quality tend to see more IC adoption of AI (e.g. my network of engineers at startups are on the whole adopting AI and using it to speed quite a few things up, though not necessarily making things higher quality). Organizations that bias towards quality often see the opposite. AI doesn't really make quality higher, or it's quite difficult to make it do so, and it can sometimes make quality on specific tasks worse because these ICs are typically really well trained for their specific task.
```

### why-are-executives-enamored-with-ai-but-ics-arent--004

`train` - `candidate` - 156 approximate tokens - 103 words

Headings: So where does the friction come from?

```markdown
# So where does the friction come from?

The difference in AI perception comes down to what work looks like at different parts of the stack. Executives manage non-deterministic systems and have built their careers around it. ICs operate in a more deterministic world and are evaluated on their ability to deliver precise, reliable output. AI fits neatly into the first worldview and awkwardly into the second.

I think this framing explains a lot of the friction that shows up when companies try to roll out AI adoption broadly. The same tool looks fundamentally different depending on what your job actually asks of you.
```

### why-are-executives-enamored-with-ai-but-ics-arent--sentence-001

`train` - `approved` - 41 approximate tokens - 27 words

Headings: (intro or continuation)

```markdown
A manager's job is to create a model of the world and align everyone's utility functions, knowing that there's a large amount of non-determinism in complex systems.
```

## Why we built 143

### why-we-built-143--001

`test` - `candidate` - 305 approximate tokens - 205 words

Headings: Where it started

```markdown
The best person to understand a problem really deeply usually isn't an engineer, it's usually someone who's using the product day in and day out with customers. Or it's the customer support person who sees questions all day about why a particular feature isn't working. While engineers have historically been the only people who could fix things, that's not true anymore.

Now with coding agents, non-engineers can fix things too and tend to be closer to the problems that users run into on a daily basis. The problem is that the tools built on top of these agents weren't made for that person, they were built for engineers by engineers. That's why we built [143](https://143.dev).

# Where it started

At Assembled, we saw this firsthand: our support and product teams kept surfacing fixes that engineers never had time for. Coding agents could have handled many of them, if the tooling didn't assume you lived in a terminal.

143 is the internal coding agent infrastructure we built at [Assembled](https://www.assembled.com) to help our non-engineers with this problem (while also helping our engineers build better software). We wanted coding agents to help with real product work, not just demos and internal tools.
```

### why-we-built-143--002

`test` - `candidate` - 343 approximate tokens - 227 words

Headings: What we built

```markdown
# What we built

We started with a small tiger team that cleaned up our instructions, invested more in CI/CD, built agent hooks, and made the agent environment less fragile. All of that helped, but it also made the bigger issue obvious: we needed a system that made this work shared across the team as opposed to being trapped inside each engineer's terminal.

We were inspired by internal systems like Stripe Minions and Ramp Inspect, but those were never available to the public. We wanted something open source that other teams could use, adapt, and improve.

We built 143 so the person who spots the bug doesn't need to become an engineer to fix it. That meant:

- **Automations shouldn't be hidden on one engineer's laptop**, so anyone on the team can see what's running and what changed.
- **Teams should be able to swap out intelligence and harnesses** as coding agents and models improve.
- **Shared context should make it natural to start work automatically** from Sentry issues, Linear assignments, PR comments, or scheduled checks.
- **Code review should be handled by agents** on some or all PRs, and they should be able to auto-approve low-risk changes against thresholds you define.
- **You should be able to set up a great environment once for everyone**, with the same repos, credentials, tools, logs, docs, and product context available to the whole team.
```

### why-we-built-143--003

`test` - `candidate` - 258 approximate tokens - 184 words

Headings: Open source for everyone

```markdown
# Open source for everyone

The same idea that you shouldn't have to be an insider to contribute is why we open-sourced 143.

I owe a lot of my career to early open-source work on Ruby on Rails. That is where I learned software fundamentals from people like Aaron Patterson, Santiago Pastorino, Jose Valim, and Jeremy Doerr. Their PR reviews, their patience, and their willingness to design-pair with strangers on the internet shaped how I think about software.

I was just a college student, but the Rails core team didn't care who I was. If a PR was good and well-intentioned, it was welcome. I started with tests and tiny refactors, learned more of the codebase, and eventually got really deep into the internals of Active Record. That work helped me get my job at Stripe and became the launching pad for the rest of my career.

I want 143 to be available in that same spirit. I hope it helps other people and teams the way open source helped me. The code is [on GitHub](https://github.com/assembledhq/143) under an MIT License.
```
