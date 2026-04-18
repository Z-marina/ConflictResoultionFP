"""
Evaluation dataset: 25 diverse conflict scenarios with ground-truth labels.
Covers bullying, physical conflict, cyberbullying, verbal harassment,
social exclusion, threats, and edge cases where the system might struggle.
"""

SCENARIOS = [
    # ── BULLYING ──────────────────────────────────────────────────────────────
    {
        "id": "B01",
        "category": "bullying",
        "difficulty": "medium",
        "description": (
            "A group of older students has been taking my lunch money every day "
            "for two weeks. Today they pushed me into a locker when I said no. "
            "I'm scared to tell a teacher because they said they'd make it worse."
        ),
    },
    {
        "id": "B02",
        "category": "bullying",
        "difficulty": "low",
        "description": (
            "My classmate keeps calling me names related to my weight in front of others. "
            "It happens almost every day and now I dread going to gym class."
        ),
    },
    {
        "id": "B03",
        "category": "bullying",
        "difficulty": "high",
        "description": (
            "I'm a bystander. I watch a kid get verbally abused at the bus stop daily "
            "by a group of five students. Yesterday they grabbed his backpack and threw "
            "it in traffic. I want to help but I'm afraid they'll turn on me."
        ),
    },

    # ── PHYSICAL CONFLICT ─────────────────────────────────────────────────────
    {
        "id": "P01",
        "category": "physical_conflict",
        "difficulty": "high",
        "description": (
            "Two of my friends got into a fistfight after school today over a rumor "
            "one of them spread. One got a bloody nose. Now both are furious and "
            "want a rematch tomorrow morning."
        ),
    },
    {
        "id": "P02",
        "category": "physical_conflict",
        "difficulty": "medium",
        "description": (
            "I shoved a kid in the hallway after he kept bumping into me on purpose. "
            "Now his friends are saying they're going to jump me after school. "
            "I feel like I have to fight back to protect myself."
        ),
    },
    {
        "id": "P03",
        "category": "physical_conflict",
        "difficulty": "low",
        "description": (
            "My lab partner and I got into a shoving match over who broke the experiment. "
            "The teacher didn't see it. We're both embarrassed but neither wants to apologize first."
        ),
    },

    # ── CYBERBULLYING ─────────────────────────────────────────────────────────
    {
        "id": "C01",
        "category": "cyberbullying",
        "difficulty": "high",
        "description": (
            "Someone made a fake Instagram account with my name and photos and is posting "
            "embarrassing edited pictures. Hundreds of students have followed the account. "
            "I know who it is but have no proof. I feel humiliated and don't want to go to school."
        ),
    },
    {
        "id": "C02",
        "category": "cyberbullying",
        "difficulty": "medium",
        "description": (
            "My ex-friend added me to a group chat just to send mean messages about me. "
            "There are 30 people in the chat, some I don't even know. Every time I leave "
            "they add me back."
        ),
    },
    {
        "id": "C03",
        "category": "cyberbullying",
        "difficulty": "low",
        "description": (
            "Someone left a really mean anonymous comment on my school project post. "
            "I think I know who it is. It hurt my feelings and I want to respond."
        ),
    },

    # ── VERBAL HARASSMENT ─────────────────────────────────────────────────────
    {
        "id": "V01",
        "category": "verbal_harassment",
        "difficulty": "medium",
        "description": (
            "A student keeps making racist jokes directed at me in class. When I ask him "
            "to stop he says I'm being too sensitive. The teacher hasn't noticed."
        ),
    },
    {
        "id": "V02",
        "category": "verbal_harassment",
        "difficulty": "low",
        "description": (
            "My classmate constantly mocks my accent whenever I answer a question. "
            "Other students laugh along. I've started avoiding participating."
        ),
    },
    {
        "id": "V03",
        "category": "verbal_harassment",
        "difficulty": "high",
        "description": (
            "I'm being harassed because of my religion. A group of students follows me "
            "between classes making slurs and mimicking prayer. It happens every single day."
        ),
    },

    # ── SOCIAL EXCLUSION ──────────────────────────────────────────────────────
    {
        "id": "S01",
        "category": "social_exclusion",
        "difficulty": "low",
        "description": (
            "My friend group suddenly stopped inviting me to things without explanation. "
            "They talk and laugh right in front of me and go quiet when I approach. "
            "I don't know what I did wrong."
        ),
    },
    {
        "id": "S02",
        "category": "social_exclusion",
        "difficulty": "medium",
        "description": (
            "I transferred schools this year and no one will let me sit with them at lunch. "
            "I eat alone every day. I've tried to introduce myself but people just walk away."
        ),
    },
    {
        "id": "S03",
        "category": "social_exclusion",
        "difficulty": "medium",
        "description": (
            "My friend is being excluded because she came out as gay. Her former friends "
            "spread rumors and convinced others not to talk to her. She's been crying "
            "every day and I don't know how to support her."
        ),
    },

    # ── THREATS ───────────────────────────────────────────────────────────────
    {
        "id": "T01",
        "category": "threat",
        "difficulty": "critical",
        "description": (
            "A student in my class said 'everyone's going to regret tomorrow' and "
            "showed someone a photo of a weapon on his phone. He seemed serious. "
            "I overheard this and I'm terrified but don't want to get him in trouble "
            "if I misunderstood."
        ),
    },
    {
        "id": "T02",
        "category": "threat",
        "difficulty": "high",
        "description": (
            "I received an anonymous text saying I'd better watch my back on Friday. "
            "I have no idea who sent it or if it's a prank. I'm anxious and can't focus."
        ),
    },
    {
        "id": "T03",
        "category": "threat",
        "difficulty": "medium",
        "description": (
            "During an argument, a student told me he knew where I lived and would "
            "make sure I regretted embarrassing him. I don't know if he means it."
        ),
    },

    # ── WEAPONS ───────────────────────────────────────────────────────────────
    {
        "id": "W01",
        "category": "weapons",
        "difficulty": "critical",
        "description": (
            "I saw a student put what looked like a knife in his locker this morning. "
            "I'm not completely sure but it looked real. He's been in several fights recently."
        ),
    },

    # ── EDGE CASES (system stress tests) ─────────────────────────────────────
    {
        "id": "E01",
        "category": "edge_ambiguous",
        "difficulty": "hard",
        "description": (
            "I don't even know if this is a real conflict. My teacher grades me lower than "
            "everyone else even when my work is the same quality. When I asked about it she "
            "got defensive. My parents think I'm imagining it."
        ),
    },
    {
        "id": "E02",
        "category": "edge_self_involved",
        "difficulty": "hard",
        "description": (
            "I'm the one who's been excluding someone and now I feel terrible about it. "
            "She used to be my best friend and I don't know why I started being mean. "
            "I want to apologize but I'm afraid she'll reject me or tell everyone."
        ),
    },
    {
        "id": "E03",
        "category": "edge_online_external",
        "difficulty": "hard",
        "description": (
            "The harassment started online but now kids from school are joining in. "
            "Some of them don't even go to my school. It's crossed into real life — "
            "someone egged my house. My parents are involved and want to call the police."
        ),
    },
    {
        "id": "E04",
        "category": "edge_vague",
        "difficulty": "hard",
        "description": "Things at school are really bad. I just need help.",
    },
    {
        "id": "E05",
        "category": "edge_mental_health",
        "difficulty": "critical",
        "description": (
            "I'm being bullied so badly that I don't want to come to school anymore. "
            "Sometimes I think everyone would be better off without me. "
            "I don't know who to talk to."
        ),
    },
]

# Ground-truth labels for classification evaluation
REPORT_LABELS = [
    {"id": "R01", "text": "someone keeps pushing me in the hallway every morning near my locker", "type": "bullying", "urgency": "medium"},
    {"id": "R02", "text": "I heard two kids planning a fight behind the gym for after school today", "type": "physical_conflict", "urgency": "high"},
    {"id": "R03", "text": "there's a fake profile of a student in 10th grade going around with edited photos", "type": "cyberbullying", "urgency": "high"},
    {"id": "R04", "text": "a kid told me he has something in his bag that will scare everyone", "type": "weapons", "urgency": "critical"},
    {"id": "R05", "text": "the new student has been eating alone and crying in the bathroom. no one talks to her", "type": "social_exclusion", "urgency": "medium"},
    {"id": "R06", "text": "someone in my class keeps making homophobic comments at another student", "type": "verbal_harassment", "urgency": "medium"},
    {"id": "R07", "text": "i got a text that said i should not come to school tomorrow if i know what's good for me", "type": "threat", "urgency": "critical"},
    {"id": "R08", "text": "there's a group chat where students are mocking a specific teacher using their real name", "type": "cyberbullying", "urgency": "low"},
    {"id": "R09", "text": "two students got into a shoving match in the cafeteria but it broke up quickly", "type": "physical_conflict", "urgency": "low"},
    {"id": "R10", "text": "a student has been coming to school with bruises and seems scared. might be from home", "type": "other", "urgency": "critical"},
]
