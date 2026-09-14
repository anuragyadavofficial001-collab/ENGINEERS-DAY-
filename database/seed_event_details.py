# ============================================================
# ENGINEERS DAY 2026
# 27 EVENT MASTER DATA SEEDER
# ============================================================

import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# FLASK APP
# ============================================================

from app import app
from database.db import get_db_connection

EVENTS = [

    {
        "name": "BGMI Tournament",
        "description": """
A competitive mobile gaming tournament focused on tactical decision-making,
team coordination, survival strategy and execution under pressure.

Participants compete in squad-based matches where communication,
positioning, resource management and final-zone decisions determine the result.
""",
        "prize_pool": "₹5,000",
        "requirements": """
• Smartphone capable of running BGMI
• Stable internet connection
• Own BGMI account
• 4 players per team
• Team communication recommended
""",
        "rules": """
1. Each team must consist of 4 players.
2. Players must use their registered accounts.
3. No hacking, scripting, exploiting bugs or unauthorized software.
4. Emulator use is not permitted unless specifically announced by organizers.
5. Teaming with another registered squad is prohibited.
6. Unsportsmanlike behaviour may result in disqualification.
7. Organizer decisions regarding match disputes will be final.
""",
        "mode": "TEAM",
        "min_team": 4,
        "max_team": 4,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Tech Treasure Hunt",
        "description": """
A technology-driven treasure hunt combining logical thinking, observation,
technical clues and collaborative problem solving.

Teams or participants solve progressive clues to unlock the next stage
and reach the final objective.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Smartphone
• Internet access when required
• Basic computer and technology awareness
• Analytical thinking
""",
        "rules": """
1. Every clue must be solved in the specified order.
2. Sharing clues with other participants is prohibited.
3. External assistance may lead to disqualification.
4. Participants must follow organizer instructions at every checkpoint.
5. The fastest valid completion wins.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Reverse Coding",
        "description": """
A programming challenge where participants analyze program behaviour,
logic and outputs before reconstructing the underlying solution.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop/Desktop
• Basic programming knowledge
• Understanding of algorithms and debugging
""",
        "rules": """
1. Participants must solve the assigned programming problems independently.
2. Internet usage will be allowed only if announced by organizers.
3. Copying another participant's solution is prohibited.
4. Malicious code or system interference is strictly prohibited.
5. Solutions will be evaluated for correctness and execution.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Business Idea Pitch",
        "description": """
A startup-oriented challenge where participants transform an idea into a
clear, practical and persuasive business proposition.

The focus is on innovation, feasibility, market understanding and pitch quality.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Business/startup idea
• Presentation material
• Market/problem understanding
• Clear pitch structure
""",
        "rules": """
1. The idea must be presented within the allocated time.
2. Participants must clearly explain the problem and proposed solution.
3. Plagiarized or copied concepts may be rejected.
4. Judges may ask follow-up questions.
5. Judges' evaluation will be final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Codeless Development",
        "description": """
A rapid innovation challenge focused on building a useful digital solution
without relying primarily on traditional programming.

Participants demonstrate how effectively modern no-code and low-code tools
can transform an idea into a working solution.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop
• Internet connection
• Familiarity with no-code/low-code platforms
• Working project concept
""",
        "rules": """
1. The solution must be created during the designated challenge period.
2. Participants must explain the tools and workflow used.
3. Pre-built projects may be demonstrated only when permitted by organizers.
4. Evaluation includes usability, creativity and implementation quality.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Content Writing",
        "description": """
A writing challenge measuring clarity, creativity, structure, originality
and the ability to communicate ideas effectively.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Pen and paper or computer as specified
• Strong written communication
• Original thinking
""",
        "rules": """
1. Content must be original.
2. Participants must follow the assigned topic.
3. Word/time limits must be respected.
4. Plagiarism will result in disqualification.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Mock Interview",
        "description": """
A simulated professional interview designed to evaluate communication,
confidence, technical awareness, problem solving and professional presence.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Resume
• Professional introduction
• Basic technical/domain knowledge
""",
        "rules": """
1. Participants must report at the assigned time.
2. Professional conduct is mandatory.
3. Evaluation may include technical and HR-style questions.
4. Judges' assessment will be final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Data Visualization Using Dashboard",
        "description": """
A data storytelling challenge where participants transform raw information
into an interactive, meaningful and visually effective dashboard.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop
• Dashboard/data visualization tool
• Basic data analysis knowledge
""",
        "rules": """
1. Participants must use the provided or approved dataset.
2. Visualizations should accurately represent the underlying data.
3. Misleading charts may receive negative evaluation.
4. Dashboard usability and insight quality will be considered.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Just A Minute (JAM)",
        "description": """
A rapid communication challenge where participants speak continuously on
a given topic while maintaining relevance, fluency and confidence.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Strong communication skills
• Quick thinking
• Topic awareness
""",
        "rules": """
1. Participants must speak on the assigned topic.
2. Unnecessary repetition should be avoided.
3. Participants must remain relevant to the topic.
4. Time limits must be strictly followed.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Rapid Fire",
        "description": """
A high-speed knowledge challenge testing reaction time, recall,
general awareness and decision making under pressure.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• General awareness
• Technology knowledge
• Quick response ability
""",
        "rules": """
1. Questions must be answered within the allotted time.
2. No external assistance is permitted.
3. The quizmaster's decision will be final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "LOGO Design",
        "description": """
A creative design challenge focused on visual identity, originality,
concept development and effective communication through a logo.
""",
        "prize_pool": "₹2,500",
        "requirements": """
• Laptop/Desktop
• Design software
• Basic graphic design knowledge
""",
        "rules": """
1. Designs must be original.
2. Submitted work must follow the assigned theme.
3. Copyrighted material should not be used without permission.
4. Judges will evaluate concept, aesthetics and relevance.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Tech Meme War",
        "description": """
A creative technology-themed meme competition combining humour,
timeliness and technical understanding.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Smartphone or laptop
• Basic image editing capability
• Creativity
""",
        "rules": """
1. Memes must be technology-related.
2. Offensive, discriminatory or abusive content is prohibited.
3. Submitted work must be original.
4. Judging will consider creativity, relevance and presentation.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Reasoning, Aptitude & GK Test",
        "description": """
A competitive assessment covering quantitative aptitude, logical reasoning,
general knowledge and problem-solving ability.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Basic mathematics
• Logical reasoning
• General awareness
""",
        "rules": """
1. The test must be completed within the assigned time.
2. No unauthorized assistance is permitted.
3. Any malpractice may result in immediate disqualification.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Poster Making",
        "description": """
A visual communication challenge where participants convert a theme or
message into an engaging and meaningful poster.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Drawing/design materials as specified
• Creative concept
• Visual communication skills
""",
        "rules": """
1. Work must be original.
2. The assigned theme must be followed.
3. Submitted work must be completed within the given time.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Web Wonder",
        "description": """
A web development challenge focused on designing and building an engaging,
functional and responsive web experience.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop
• HTML/CSS/JavaScript knowledge
• Basic web development skills
""",
        "rules": """
1. The website must satisfy the assigned challenge requirements.
2. Code should be substantially created by the participant.
3. External libraries may be used where permitted.
4. Evaluation includes functionality, UI/UX and originality.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "AD - Mad Show",
        "description": """
A performance-based advertising challenge where participants create and
present an entertaining advertisement around a given concept or product.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Performance team/material as applicable
• Creative concept
• Presentation skills
""",
        "rules": """
1. Performance must remain within the allocated time.
2. Content must remain appropriate for a college event.
3. Judges will evaluate creativity, delivery and impact.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "ChatGPT Prompt Challenge",
        "description": """
A modern AI challenge focused on prompt engineering, reasoning,
instruction design and the ability to obtain reliable outputs from AI systems.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop or smartphone
• Internet access
• Basic understanding of generative AI
• Prompt engineering skills
""",
        "rules": """
1. Participants must follow the challenge prompt and time limits.
2. Prompts and outputs may be evaluated together.
3. Attempts to manipulate the competition environment are prohibited.
4. Final evaluation will consider quality, precision and creativity.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Coding & Debugging",
        "description": """
A practical programming challenge testing implementation ability,
logical reasoning and debugging under time constraints.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Laptop/Desktop
• Programming knowledge
• Debugging skills
""",
        "rules": """
1. Participants must solve the assigned problems within the time limit.
2. Malicious code is strictly prohibited.
3. Copying another participant's solution is not allowed.
4. Correctness and efficiency may both be considered.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Pictionary",
        "description": """
A visual guessing challenge that combines drawing speed, interpretation
and communication without relying on spoken explanations.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Drawing medium as specified
• Creativity
• Quick interpretation
""",
        "rules": """
1. Drawings must communicate the assigned word/concept.
2. Verbal clues may be restricted according to the round.
3. Time limits must be followed.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Group Discussion",
        "description": """
A structured discussion challenge evaluating communication, listening,
reasoning, leadership, teamwork and the ability to build arguments.
""",
        "prize_pool": "₹2,000",
        "requirements": """
• Communication skills
• Topic awareness
• Logical reasoning
""",
        "rules": """
1. Participants must maintain respectful discussion.
2. Personal attacks are prohibited.
3. Participants should support arguments with reasoning.
4. Judges will evaluate individual contribution and discussion quality.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Debate",
        "description": """
A competitive argumentation event focused on structured reasoning,
evidence, rebuttal and persuasive communication.
""",
        "prize_pool": "₹2,500",
        "requirements": """
• Communication skills
• Topic awareness
• Argument construction
""",
        "rules": """
1. Participants must argue the assigned position.
2. Arguments must remain respectful.
3. Personal attacks and abusive language are prohibited.
4. Judges' decision will be final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Project Presentation",
        "description": """
A technical presentation platform where participants demonstrate a project,
explain its architecture, implementation, impact and future scope.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Working/project prototype
• Presentation deck
• Technical explanation
""",
        "rules": """
1. Participants must present within the allocated time.
2. Project ownership and contribution should be clearly stated.
3. Judges may ask technical questions.
4. Evaluation includes innovation, implementation and presentation.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "PPT Presentation",
        "description": """
A presentation challenge measuring storytelling, slide design,
communication and the ability to explain a topic effectively.
""",
        "prize_pool": "₹2,500",
        "requirements": """
• Laptop
• Presentation deck
• Strong communication skills
""",
        "rules": """
1. Presentation duration must be respected.
2. Slides should be relevant to the selected topic.
3. Plagiarism should be avoided.
4. Judges' decision is final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "SR Got Talent",
        "description": """
A stage platform celebrating creativity and individual talent across
performance, music, art, entertainment and other approved categories.
""",
        "prize_pool": "₹3,000",
        "requirements": """
• Performance material/instrument where required
• Stage-ready presentation
• Original performance
""",
        "rules": """
1. Performance must stay within the assigned time.
2. Content must be appropriate for the event.
3. Dangerous acts require prior approval.
4. Judges' decision will be final.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Capture The Flag (CTF)",
        "description": """
A cybersecurity challenge built around finding hidden flags through
security puzzles, digital investigation, cryptography and logical exploitation.
""",
        "prize_pool": "₹4,000",
        "requirements": """
• Laptop
• Internet/network access as provided
• Basic cybersecurity knowledge
• Familiarity with web, cryptography or forensics concepts
""",
        "rules": """
1. Participants may attack only systems explicitly provided for the challenge.
2. Attacking college infrastructure or external systems is prohibited.
3. Sharing flags between participants is prohibited.
4. Automated abuse intended to disrupt the platform is prohibited.
5. Highest valid score within the time limit wins.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Free Fire (Online Game)",
        "description": """
A competitive online battle royale tournament focused on teamwork,
game sense, tactical execution and survival performance.
""",
        "prize_pool": "₹5,000",
        "requirements": """
• Compatible smartphone
• Stable internet connection
• Free Fire account
• 4 players per team
""",
        "rules": """
1. Each team must consist of 4 players.
2. Players must use their registered accounts.
3. Cheats, scripts, hacks or unauthorized modifications are prohibited.
4. Match instructions issued by organizers must be followed.
5. Disputes must be reported through the official event process.
""",
        "mode": "TEAM",
        "min_team": 4,
        "max_team": 4,
        "winner_certificate": True,
        "runner_certificate": True,
    },

    {
        "name": "Hackathon",
        "description": """
A build-focused innovation sprint where participants transform a real-world
problem into a working technology solution within a limited time window.

The event emphasizes ideation, implementation, collaboration, usability
and demonstrable impact.
""",
        "prize_pool": "₹10,000",
        "requirements": """
• Laptop
• Development environment
• Internet connection
• Working project/prototype
• Technical presentation
""",
        "rules": """
1. The solution must address the announced challenge or theme.
2. Participants must respect the submission deadline.
3. Third-party tools and APIs must be disclosed where required.
4. Plagiarism or misrepresentation of work may result in disqualification.
5. Judges will evaluate innovation, technical implementation, usability,
   feasibility and presentation.
""",
        "mode": "INDIVIDUAL",
        "min_team": None,
        "max_team": None,
        "winner_certificate": True,
        "runner_certificate": True,
    },
]


def seed_event_details():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        updated = 0
        missing = []

        for event in EVENTS:

            cursor.execute(
                """
                SELECT id
                FROM games
                WHERE game_name = %s
                LIMIT 1
                """,
                (event["name"],)
            )

            existing = cursor.fetchone()

            if not existing:
                missing.append(event["name"])
                continue

            cursor.execute(
                """
                UPDATE games
                SET
                    description = %s,
                    prize_pool = %s,
                    requirements = %s,
                    rules = %s,
                    registration_mode = %s,
                    team_min_size = %s,
                    team_max_size = %s,
                    winner_certificate = %s,
                    runner_up_certificate = %s
                WHERE id = %s
                """,
                (
                    event["description"].strip(),
                    event["prize_pool"],
                    event["requirements"].strip(),
                    event["rules"].strip(),
                    event["mode"],
                    event["min_team"] or 0,
                    event["max_team"] or 0,
                    event["winner_certificate"],
                    event["runner_certificate"],
                    existing["id"],
                )
            )

            updated += 1

        connection.commit()

        print("=" * 60)
        print("ENGINEERS DAY 2026 — EVENT DATA UPDATE")
        print("=" * 60)
        print(f"Events updated : {updated}")
        print(f"Events missing : {len(missing)}")

        if missing:
            print("\nMissing events:")
            for name in missing:
                print(" -", name)

        print("\nDone.")

    except Exception as exc:

        if connection:
            connection.rollback()

        print("\nERROR:", exc)
        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    with app.app_context():
        seed_event_details()