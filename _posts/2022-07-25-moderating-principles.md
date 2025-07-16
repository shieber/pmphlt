---
layout: post
title: "Moderating principles"
date: 2022-07-25 08:00:00 -04:00
categories: [computational linguistics, computer science, language, open access, scholarly communication, writing]
tags: [arxiv, moderation, scholarly communication, computational linguistics]
---

Some time around April 1994, I founded the Computation and Language
E-Print Archive, the first preprint repository for a subfield of
computer science. It was hosted on Paul Ginsparg's [arXiv
platform](https://arxiv.org/), which at the time had been hosting only
physics papers, built out from the original arXiv repository for
high-energy physics theory, hep-th. The repository, cmp-lg (as it was
then called), was superseded in 1999 by an open-access preprint
repository for all of computer science, the [Computing Research
Repository (CoRR)](https://arxiv.org/corr), which covered a broad
range of subject areas, including computation and language. The CoRR
organizing committee also decided to host CoRR on arXiv. I switched
over to moderating for the CoRR repository from cmp-lg, and have
continued to do so for the last – oh my god – 22 years.[^1]

Articles in the arXiv are classified with a single primary *subject
class*, and may have other subject classes as secondary. The
switchover folded cmp-lg into the arXiv as articles tagged with the
[cs.CL (computation and language) subject
class](https://arxiv.org/archive/cs.CL). I thus became the moderator
for cs.CL.

A preprint repository like the arXiv is not a journal. There is no
peer review applied to articles. There is essentially no quality
control. That is not the role of a preprint repository. The role of a
preprint repository is open distribution, not vetting. Nonetheless,
*some* kind of control is needed in making sure that, at the very
least, the documents being submitted are in fact scholarly articles
and are appropriately tagged as to subfield, and that need has
expanded with the dramatic increase in submissions to CoRR over the
years. The primary duty of a moderator is to perform this vetting and
triage: verifying that a submission possesses the minimum standards
for being characterized as a scholarly article, and that it falls
within the purview of, say, cs.CL, as a primary or secondary subject
class.

I am (along with the other arXiv moderators) thus regularly in the
position of having to make decisions as to whether a document is a
scholarly article or not. To a large extent, Justice Potter Stewart's
approach works reasonably well for scholarly articles: you know them
when you see them. But over time, as more marginal cases come up, I've
felt that tracking my thinking on the matter would be useful for
maintaining consistency in my own practice. And now that I've done
that for a while, I thought it might be useful to share my approach
more broadly. That is the goal of this post.

The following thus constitutes (some of) the de facto policies that I
use in making decisions as the moderator for the cs.CL collection in
the CoRR part of the arXiv repository. I emphasize that these are *my*
policies, not those of CoRR or the moderators of other CoRR
subjects. (The arXiv folks themselves provide a more general [guide
for arXiv moderators](https://arxiv.org/help/moderators).)

<!--more-->

## What's a scholarly article?

To qualify for inclusion, a submission must constitute a scholarly
article. For this purpose, scholarly articles fall into three classes:

### Analytic

The submission presents a *specific question that it then
answers*. This might take the form of presenting a proposition and
then proving it, or presenting an alternative method for a task and
then demonstrating that it does or does not improve over some other
method, or defining a new task and presenting a method for carrying it
out. It ought to present enough of a clue about the methods such that
at least the beginning of an attempt at replication could be made. On
the other hand, the reported result need not be novel, or interesting,
or even correct. Determining whether a result is novel, interesting,
or correct is the point of reviewing, which, remember, we are not in
the business of.

### Synthetic

The submission *synthesizes in a systematic manner* other scholarly
articles. (Yes, this definition is intentionally recursive, with
analytic articles forming the base case.) Review articles fall within
this class. The article should make at least an attempt at both
systematicity (providing and using a well-formed taxonomy, for
instance) and exhaustiveness.

### Dataset

Occasionally, we get papers that describe a new *publicly available
language-related dataset* of interest, with perhaps only rudimentary
analysis of the data. These can be appropriate if the data is made
openly available, and the availability is clearly featured in the
article.

Papers that don't arguably fall into one of these three classes I will
typically reject for inclusion in cs.CL. In particular, I frequently
see articles whose putative thesis is (as far as I can tell) "I did a
thing". Typically, the paper reports that "I built a piece of software
that does *X*." A report of that sort does not suffice as constituting
a scholarly article. A special case of this is the putative dataset
paper that reports "I built a corpus" but provides no access to that
corpus.

## What's a CL (computation and language) article?

Computational linguistics (CL) is the scholarly field studying human
(natural) language using the tools and techniques of computer science,
and is allied with the engineering field of natural-language
processing (NLP), the building or improving of useful artifacts that
manipulate natural language. Articles appropriate for a cs.CL tag,
then, should have something to do with natural language. Articles
about sound processing of speech may be appropriate if the techniques
rely on the fact that the acoustic signal is spoken
language. Similarly for image processing.

I tend to apply an extremely broad interpretation of "having something
to do with language", especially for cross-listing as a cs.CL
secondary subject class, on the theory that errors of omission are
worse than errors of commission for subscribers to the cs.CL
notifications.

In addition, articles need to involve some computer science. CoRR is,
after all, a computer science repository. Formal analysis of language
that merely uses computers for the analysis does not by itself qualify
a paper as involving computer science. After all, these days, all
scientific research involves computers. I've rejected some excellent
papers in what is essentially formal linguistics because they involved
no nontrivial involvement of computer science ideas. Similarly, we get
papers that apply well-known and standard NLP methods to standard NLP
problems in some application area, such as analyzing health records or
student writing, where the (potential) contribution is to health or
education. Absent *some* involvement with computer science, these
articles are best thought of as falling within the application
field. Such articles deserve distribution in a preprint repository,
just not CoRR. Health application papers might use
[medRxiv](https://www.medrxiv.org/), education papers
[EdArXiv](https://edarxiv.org/). Sadly, there are many fields of
scholarship without good, long-term, well-maintained repositories, but
CoRR can't be the solution to *that* problem. (The open-field
[Zenodo](https://zenodo.org/) repository should serve for most such
papers.)

## Special cases

There are tricky cases that arise with sufficient frequency that they
are worth considering explicitly.

### Research proposals

We often see articles (typically very short ones, two or three pages)
sketching an idea for dealing with some problem or other, but without
presenting any results. These may even be published in a workshop or
conference proceedings, and perhaps the ideas may be novel and worth
following up on. Nonetheless, without substantive results they don't
qualify as scholarly articles. The authors could of course perform the
follow-up and then submit an article describing the results (whether
positive or negative). Of course, more fully worked out proposals with
useful details might be acceptable.

### Course projects

Submissions describing course projects or other schoolwork
(undergraduate or master's theses, for example) may be allowable for
inclusion if they are otherwise structured as scholarly articles and
meet the criteria above. However, they may require extra scrutiny to
verify the criteria described above.

### Predatory journals

Publication in a predatory journal (a faux journal charging for
article processing while providing no or only perfunctory reviewing
and other publishing services) is, by arXiv policy, not grounds for
rejecting an article. However, such submissions often carry copyright
notices, which arXiv disallows, and the submissions also often fail
the criteria for being a scholarly article above.

### Hyper-interdisciplinary articles

We sometimes get articles that are what might be charitably referred
to as "hyper-interdisciplinary", in bringing together a CL topic with
some other distant topic, a theory of language meaning based on a
cylindrical algebraic reconstruction of quantum gravity, say. Such an
article is difficult if not impossible to determine the status of: is
it a scholarly article or a crankish manifesto? These articles are
typically rejected. I simply do not have the time or inclination to
attempt to reconstruct an understanding of the article to determine
whether it is appropriate for cs.CL.

Perhaps in doing so, I am eliminating from the repository the one true
breakthrough in cracking the nut of the hardest intellectual problem
of human cognition – how language works. Perhaps, but the author might
have managed to express it in terms that a computer scientist
specializing in natural language can understand. In any case, nothing
prevents the author from submitting the article to a journal for peer
review and making his[^2] case.

---

[^1]: Thanks to Yonatan Belinkov, Karina Halevy, and Joe Halpern for their helpful comments on earlier drafts of this post.

[^2]: These submissions are always solo authored by men. 
