import os
import re
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from nlu_utils import extract_intent, extract_entities, analyze_sentiment, get_follow_up_question

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Set the session lifetime to 3 hours (adjust as needed)
app.permanent_session_lifetime = timedelta(hours=3)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define a User model with name, email, and password_hash
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

# Comprehensive response templates for mental health issues
RESPONSES = {
    "loneliness": {
        "positive": (
            "🌱 I notice you're experiencing some loneliness but maintaining a positive outlook, which is a strength. "
            "Consider building on this by:\n\n"
            "1️⃣ Scheduling regular virtual or in-person meetups with friends\n"
            "2️⃣ Joining community groups aligned with your interests\n"
            "3️⃣ Volunteering for causes you care about\n\n"
            "✨ These activities can deepen your sense of connection. Remember that quality relationships often develop gradually. "
            "💡 If loneliness persists, consulting with a therapist like Dr. Sarah Chen, who specializes in interpersonal connections, could provide personalized strategies."
        ),
        "neutral": (
            "🧩 Feeling lonely is a common human experience. To address this, you might:\n\n"
            "1️⃣ Reach out to one person you trust each day\n"
            "2️⃣ Join a class or group that meets regularly\n"
            "3️⃣ Practice self-compassion when feelings of loneliness arise\n\n"
            "⏳ Building meaningful connections takes time, so be patient with yourself. "
            "📱 Applications like Meetup or community center bulletin boards can help you find groups with shared interests. "
            "🔍 If loneliness continues to affect your daily life, consider speaking with a counselor like Dr. James Wilson, who specializes in social connection."
        ),
        "negative": (
            "💙 I'm truly sorry you're experiencing such profound loneliness. This feeling can be overwhelming and painful. "
            "When loneliness feels this intense, immediate steps might include:\n\n"
            "1️⃣ Calling a supportive friend or family member\n"
            "2️⃣ Contacting a crisis helpline like the Crisis Text Line (text HOME to 741741)\n"
            "3️⃣ Scheduling an appointment with a mental health professional\n\n"
            "🌟 Please know that deep loneliness can be addressed with proper support. "
            "👩‍⚕️ Dr. Lisa Rodriguez specializes in isolation and loneliness issues and offers both in-person and telehealth appointments. "
            "🔆 Remember that reaching out for help is a sign of strength, not weakness."
        )
    },
    "depression": {
        "positive": (
            "🌻 I appreciate your openness about your feelings while maintaining some positive perspective. "
            "For managing mild depressive symptoms, consider:\n\n"
            "1️⃣ Maintaining a regular sleep schedule\n"
            "2️⃣ Engaging in 30 minutes of physical activity daily\n"
            "3️⃣ Practicing mindfulness meditation using apps like Headspace or Calm\n\n"
            "📊 Tracking your mood with an app like MoodKit can help identify patterns. "
            "👨‍⚕️ If you notice your symptoms changing, Dr. Michael Thompson specializes in mood disorders and can provide professional guidance."
        ),
        "neutral": (
            "🌧️ Depression can make everyday tasks feel much harder. Some evidence-based approaches include:\n\n"
            "1️⃣ Setting small, achievable daily goals\n"
            "2️⃣ Establishing a routine with regular meals and sleep times\n"
            "3️⃣ Limiting alcohol and caffeine consumption\n"
            "4️⃣ Connecting with at least one supportive person regularly\n\n"
            "📝 Remember that depression is a medical condition, not a personal failing. "
            "👩‍⚕️ Consider reaching out to Dr. Rebecca Lee, who uses cognitive behavioral therapy techniques for depression management. "
            "🤝 Organizations like the Depression and Bipolar Support Alliance also offer peer support groups that many find helpful."
        ),
        "negative": (
            "💜 I'm truly sorry you're experiencing such intense depressive symptoms. When depression feels this severe, please prioritize your safety. "
            "If you're having thoughts of harming yourself, please contact the National Suicide Prevention Lifeline at 988 immediately.\n\n"
            "For immediate relief:\n"
            "1️⃣ Reach out to someone you trust\n"
            "2️⃣ Focus on getting through just the next hour rather than the whole day\n"
            "3️⃣ Remove any potentially harmful items from your environment\n\n"
            "👨‍⚕️ Dr. David Kim specializes in treatment-resistant depression and offers urgent appointments. "
            "✨ Remember that severe depression is highly treatable with proper support, and many people recover completely."
        )
    },
    "anxiety": {
        "positive": (
            "🌈 I notice you're managing anxiety while maintaining perspective, which is impressive. "
            "To build on your coping skills:\n\n"
            "1️⃣ Practice progressive muscle relaxation daily\n"
            "2️⃣ Use the 5-4-3-2-1 grounding technique when anxiety spikes (identify 5 things you can see, 4 things you can touch, etc.)\n"
            "3️⃣ Consider keeping an anxiety journal to track triggers and successful coping strategies\n\n"
            "🤖 Apps like Woebot can provide in-the-moment cognitive behavioral therapy techniques. "
            "👩‍⚕️ Dr. Jennifer Patel specializes in anxiety management and can help refine your approach if needed."
        ),
        "neutral": (
            "🧠 Anxiety can be uncomfortable but is manageable with proper techniques. You might try:\n\n"
            "1️⃣ Practicing box breathing (inhale for 4 counts, hold for 4, exhale for 4, hold for 4)\n"
            "2️⃣ Challenging anxious thoughts by asking 'What's the evidence for and against this worry?'\n"
            "3️⃣ Gradually exposing yourself to situations that cause mild anxiety while using relaxation techniques\n\n"
            "🚶‍♀️ Physical exercise is also proven to reduce anxiety symptoms. "
            "👨‍⚕️ Dr. Thomas Chen specializes in anxiety disorders and can provide personalized treatment options, including both therapy and medication if appropriate."
        ),
        "negative": (
            "💙 I'm so sorry you're experiencing such intense anxiety. When anxiety feels overwhelming:\n\n"
            "1️⃣ Focus first on slow, deep breathing - inhale for 4 counts, hold for 1, exhale for 6\n"
            "2️⃣ Identify and name what you're feeling as specifically as possible\n"
            "3️⃣ Move your body gently – even just walking around the room can help reduce the physical symptoms\n\n"
            "⚡ If you're experiencing panic attacks, remember they always pass and aren't physically dangerous. "
            "👩‍⚕️ Dr. Maria Sanchez specializes in severe anxiety and panic disorders and offers same-week appointments. "
            "✨ Please consider reaching out, as severe anxiety responds very well to proper treatment."
        )
    },
    "stress": {
        "positive": (
            "🌱 It sounds like you're handling stress relatively well while recognizing its impacts. "
            "To enhance your stress management:\n\n"
            "1️⃣ Schedule regular 'worry time' – 15 minutes daily to address concerns, then set them aside\n"
            "2️⃣ Practice time-blocking your schedule to prevent multitasking\n"
            "3️⃣ Identify energy-draining activities and delegate when possible\n\n"
            "⏱️ The Pomodoro technique (25 minutes of focused work followed by a 5-minute break) can also help manage workload stress. "
            "👨‍⚕️ Dr. Robert Johnson specializes in stress management and work-life balance if you'd like professional guidance."
        ),
        "neutral": (
            "⚖️ Stress is our body's response to demands, and finding balance is key. Consider:\n\n"
            "1️⃣ Creating clear boundaries between work and personal time\n"
            "2️⃣ Practicing brief mindfulness exercises during transitions between activities\n"
            "3️⃣ Identifying your stress warning signs (headaches, irritability, etc.) to catch stress early\n"
            "4️⃣ Ensuring you get 7-9 hours of sleep\n\n"
            "🧘‍♀️ Activities like yoga, tai chi, or leisurely walking combine physical movement with mindfulness for effective stress reduction. "
            "👩‍⚕️ Dr. Alicia Wong specializes in stress-related conditions and can help develop a personalized stress management plan."
        ),
        "negative": (
            "💜 I'm truly sorry you're under such extreme stress. When stress feels overwhelming:\n\n"
            "1️⃣ Focus first on basic self-care – proper meals, hydration, and rest\n"
            "2️⃣ Temporarily reduce commitments where possible\n"
            "3️⃣ Break large problems into smaller, manageable tasks\n"
            "4️⃣ Reach out to your support network for specific help\n\n"
            "⚠️ Chronic severe stress can impact your physical health, so please prioritize addressing it. "
            "👨‍⚕️ Dr. William Park specializes in chronic stress and burnout recovery and offers both immediate coping strategies and longer-term resilience building. "
            "💼 Many employers also offer Employee Assistance Programs providing free confidential counseling."
        )
    },
    "ptsd": {
        "positive": (
            "🌟 I appreciate your resilience in dealing with trauma. For continued healing:\n\n"
            "1️⃣ Maintain your established safety practices\n"
            "2️⃣ Continue engaging with supportive communities\n"
            "3️⃣ Practice sensory grounding techniques when memories arise\n\n"
            "📱 The PTSD Coach app offers evidence-based tools for managing symptoms. "
            "👩‍⚕️ Dr. Sophia Martinez specializes in trauma-informed care and can provide trauma-specific therapies like EMDR or CPT if helpful."
        ),
        "neutral": (
            "🧠 Trauma responses are normal reactions to abnormal situations. Some helpful approaches include:\n\n"
            "1️⃣ Establishing predictable routines to create a sense of safety\n"
            "2️⃣ Learning to recognize triggers and developing a safety plan for each\n"
            "3️⃣ Practicing dual awareness when flashbacks occur (acknowledging the memory while staying grounded in the present)\n"
            "4️⃣ Connecting with others who understand trauma responses\n\n"
            "👨‍⚕️ Dr. Nathan Williams specializes in trauma recovery and offers evidence-based treatments like Prolonged Exposure therapy and EMDR."
        ),
        "negative": (
            "💙 I'm deeply sorry you're experiencing such difficult trauma symptoms. When trauma responses feel overwhelming:\n\n"
            "1️⃣ Focus first on your immediate safety\n"
            "2️⃣ Use the 5-4-3-2-1 grounding technique to reconnect with the present moment\n"
            "3️⃣ Wrap yourself in a blanket or hold a cold object to anchor yourself physically\n"
            "4️⃣ Remind yourself that you've survived the trauma and are now safe\n\n"
            "🔍 The National Center for PTSD offers crisis resources at www.ptsd.va.gov. "
            "👩‍⚕️ Dr. Elena Rodriguez specializes in complex trauma and offers trauma-sensitive approaches to healing. PTSD is treatable, and recovery is possible."
        )
    },
    "grief": {
        "positive": (
            "🕊️ I can see you're finding ways to cope with your loss while honoring your grief. "
            "As you continue healing:\n\n"
            "1️⃣ Allow yourself to celebrate good moments without guilt\n"
            "2️⃣ Create meaningful rituals to honor your loved one\n"
            "3️⃣ Consider joining a grief support group to connect with others who understand\n\n"
            "🌊 Remember that grief often comes in waves rather than linear stages. "
            "👨‍⚕️ Dr. Samuel Johnson specializes in grief counseling and can help navigate the complex emotions that may arise."
        ),
        "neutral": (
            "🍂 Grief is a natural response to loss, and everyone experiences it differently. "
            "Some approaches that might help:\n\n"
            "1️⃣ Express your feelings through journaling, art, or conversation\n"
            "2️⃣ Be patient with yourself on difficult days\n"
            "3️⃣ Maintain basic self-care routines\n"
            "4️⃣ Accept that grief may resurface around anniversaries or holidays\n\n"
            "📚 The book 'It's OK That You're Not OK' by Megan Devine offers compassionate guidance. "
            "👩‍⚕️ Dr. Sarah Williams specializes in grief counseling and can provide professional support if needed."
        ),
        "negative": (
            "💜 I'm truly sorry for your profound loss and the pain you're experiencing. "
            "When grief feels unbearable:\n\n"
            "1️⃣ Focus on just getting through this moment rather than thinking too far ahead\n"
            "2️⃣ Reach out to someone who will simply listen without trying to fix your feelings\n"
            "3️⃣ Give yourself permission to grieve in whatever way feels natural\n"
            "4️⃣ Consider contacting a grief counselor or hospice grief support services\n\n"
            "👩‍⚕️ Dr. Jessica Chen specializes in complicated grief and provides compassionate support. "
            "🤝 The organization GriefShare also offers local support groups where many find comfort in shared experiences."
        )
    },
    "addiction": {
        "positive": (
            "🌱 I appreciate your awareness and positive steps toward addressing addiction concerns. "
            "To continue your progress:\n\n"
            "1️⃣ Identify and strengthen your specific reasons for change\n"
            "2️⃣ Build a broader support network, including both professional help and peer support\n"
            "3️⃣ Develop additional healthy coping strategies for triggers\n\n"
            "🧠 The SMART Recovery program offers science-based tools for addiction recovery. "
            "👨‍⚕️ Dr. Marcus Lee specializes in addiction medicine and can provide medical support if needed."
        ),
        "neutral": (
            "⚖️ Addressing addiction requires both compassion and practical strategies. "
            "Some helpful approaches include:\n\n"
            "1️⃣ Honestly assessing how substance use is affecting different areas of your life\n"
            "2️⃣ Identifying specific triggers and creating a plan for each\n"
            "3️⃣ Exploring both professional treatment options and peer support groups\n"
            "4️⃣ Practicing stress management techniques like meditation or exercise\n\n"
            "📞 The Substance Abuse and Mental Health Services Administration (SAMHSA) offers a 24/7 helpline at 1-800-662-HELP. "
            "👩‍⚕️ Dr. Rachel Foster specializes in addiction treatment and can help determine the best approach for your situation."
        ),
        "negative": (
            "💙 I'm truly sorry you're struggling with addiction. When substance use feels overwhelming:\n\n"
            "1️⃣ Remember that addiction is a medical condition, not a moral failing\n"
            "2️⃣ Consider reaching out to SAMHSA's National Helpline at 1-800-662-HELP for immediate support\n"
            "3️⃣ If you're experiencing withdrawal symptoms, seek medical attention as some withdrawals can be dangerous\n"
            "4️⃣ Know that recovery is possible even after multiple attempts\n\n"
            "👨‍⚕️ Dr. Michael Chen specializes in addiction medicine and offers both medication-assisted treatment and therapy options. "
            "💰 Many treatment centers also offer financial assistance or sliding scale fees."
        )
    },
    "relationship": {
        "positive": (
            "💫 I notice you're taking a thoughtful approach to your relationship situation. "
            "To continue building healthy connections:\n\n"
            "1️⃣ Practice assertive communication using 'I' statements\n"
            "2️⃣ Establish clear boundaries that honor both your needs and others'\n"
            "3️⃣ Schedule regular check-ins with your partner to discuss concerns before they escalate\n\n"
            "📚 The book 'The Seven Principles for Making Marriage Work' by John Gottman offers evidence-based relationship strategies. "
            "👩‍⚕️ Dr. Lisa Patel specializes in couples counseling and can provide additional tools if needed."
        ),
        "neutral": (
            "🔄 Relationships naturally go through challenges and transitions. Some helpful approaches include:\n\n"
            "1️⃣ Identifying specific relationship patterns rather than focusing only on individual incidents\n"
            "2️⃣ Practicing active listening without planning your response\n"
            "3️⃣ Taking short breaks when discussions become heated\n"
            "4️⃣ Finding activities that bring you together in positive ways\n\n"
            "🌐 The Gottman Institute website offers free relationship resources. "
            "👨‍⚕️ Dr. James Anderson specializes in relationship counseling and can help navigate complex relationship dynamics."
        ),
        "negative": (
            "💜 I'm truly sorry you're experiencing such difficult relationship challenges. When relationship distress feels overwhelming:\n\n"
            "1️⃣ Prioritize your physical and emotional safety above all else\n"
            "2️⃣ Establish clear boundaries about acceptable behavior\n"
            "3️⃣ Consider whether temporary distance might help provide clarity\n"
            "4️⃣ Seek support from trusted friends or family\n\n"
            "⚠️ If there's any physical or emotional abuse, the National Domestic Violence Hotline is available 24/7 at 1-800-799-7233. "
            "👩‍⚕️ Dr. Emily Washington specializes in relationship crisis intervention and can provide immediate strategies as well as longer-term support."
        )
    },
    "breakup": {
        "positive": (
            "🌱 I can see you're processing your breakup with some perspective, which shows emotional strength. "
            "To continue healing:\n\n"
            "1️⃣ Acknowledge your progress while allowing yourself to experience difficult emotions when they arise\n"
            "2️⃣ Rediscover activities and interests that may have been set aside during the relationship\n"
            "3️⃣ Consider what you've learned about yourself and your needs for future relationships\n\n"
            "👨‍⚕️ Dr. Thomas Rivera specializes in life transitions and can help navigate this new chapter."
        ),
        "neutral": (
            "🧩 Breakups can be deeply challenging even when they're for the best. Some helpful approaches include:\n\n"
            "1️⃣ Giving yourself permission to grieve the relationship while creating a new routine\n"
            "2️⃣ Setting boundaries around contact with your ex-partner that protect your emotional wellbeing\n"
            "3️⃣ Leaning on your support network without feeling you must always appear 'over it'\n"
            "4️⃣ Being patient with the healing process\n\n"
            "📚 The book 'Rebuilding When Your Relationship Ends' by Bruce Fisher offers a structured approach to healing. "
            "👩‍⚕️ Dr. Olivia Martinez specializes in breakup recovery and can provide professional guidance if needed."
        ),
        "negative": (
            "💙 I'm truly sorry you're experiencing such profound pain after your breakup. "
            "When the hurt feels overwhelming:\n\n"
            "1️⃣ Focus on basic self-care like eating regularly and getting rest\n"
            "2️⃣ Consider temporarily limiting social media to avoid additional triggers\n"
            "3️⃣ Allow yourself to fully express your emotions in private or with trusted supporters\n"
            "4️⃣ Remember that intense emotional pain does eventually subside with time and proper support\n\n"
            "👨‍⚕️ Dr. Daniel Kim specializes in breakup trauma and offers both immediate coping strategies and longer-term healing techniques. "
            "🤝 Many people find that joining a support group helps them feel less alone during this difficult time."
        )
    },
    "insomnia": {
        "positive": (
            "✨ I appreciate your proactive approach to addressing your sleep concerns. "
            "To further improve your sleep quality:\n\n"
            "1️⃣ Maintain your consistent sleep schedule even on weekends\n"
            "2️⃣ Create a 30-minute wind-down routine before bed without screens\n"
            "3️⃣ Consider sleep restriction therapy, which temporarily reduces time in bed to build stronger sleep drive\n\n"
            "📱 The CBT-i Coach app offers evidence-based sleep improvement techniques. "
            "👩‍⚕️ Dr. Angela Wei specializes in sleep medicine and can provide additional personalized strategies."
        ),
        "neutral": (
            "🌙 Sleep difficulties can significantly impact daily functioning. Some evidence-based approaches include:\n\n"
            "1️⃣ Establishing a consistent sleep schedule seven days a week\n"
            "2️⃣ Creating a bedroom environment that's cool, dark, and quiet\n"
            "3️⃣ Avoiding caffeine after noon and alcohol within 3 hours of bedtime\n"
            "4️⃣ Getting out of bed if you're unable to fall asleep within 20 minutes\n\n"
            "🧠 Cognitive Behavioral Therapy for Insomnia (CBT-I) is considered the first-line treatment for chronic insomnia. "
            "👨‍⚕️ Dr. Robert Johnson specializes in sleep disorders and can provide comprehensive assessment and treatment."
        ),
        "negative": (
            "💜 I'm truly sorry you're struggling with such severe sleep issues. Ongoing insomnia can be extremely distressing. "
            "For immediate relief:\n\n"
            "1️⃣ Focus on rest rather than sleep – lying quietly with eyes closed still provides some rejuvenation\n"
            "2️⃣ Avoid checking the time during the night, which increases anxiety\n"
            "3️⃣ Practice gentle relaxation techniques like progressive muscle relaxation\n"
            "4️⃣ Consider speaking with a healthcare provider about short-term medication options while developing long-term sleep skills\n\n"
            "👩‍⚕️ Dr. Michelle Park specializes in complex sleep disorders and can help determine if underlying issues like sleep apnea might be contributing to your insomnia."
        )
    },
    "eating_disorder": {
        "positive": (
            "🌱 I appreciate your awareness and efforts regarding your eating patterns. "
            "To support continued healing:\n\n"
            "1️⃣ Work with a registered dietitian who specializes in eating disorders to develop a flexible, nourishing meal plan\n"
            "2️⃣ Practice identifying emotions that trigger eating disorder thoughts\n"
            "3️⃣ Continue building a support network that understands eating disorder recovery\n\n"
            "🔄 Recovery is rarely linear, so self-compassion during setbacks is essential. "
            "👩‍⚕️ Dr. Sarah Miller specializes in eating disorder treatment and can provide comprehensive care."
        ),
        "neutral": (
            "⚖️ Concerns about eating patterns deserve compassionate attention. Some helpful approaches include:\n\n"
            "1️⃣ Seeking assessment from healthcare providers with eating disorder expertise\n"
            "2️⃣ Working toward regular, adequate nutrition with professional guidance\n"
            "3️⃣ Identifying underlying emotions or beliefs that may be fueling disordered eating\n"
            "4️⃣ Connecting with others in recovery through organizations like the National Eating Disorders Association\n\n"
            "✨ Recovery is absolutely possible with proper support. "
            "👩‍⚕️ Dr. Jessica Chen specializes in eating disorder treatment and offers evidence-based approaches like Enhanced Cognitive Behavioral Therapy."
        ),
        "negative": (
            "💙 I'm deeply concerned about your struggles with eating and want you to know that help is available. "
            "When eating disorder symptoms are severe:\n\n"
            "1️⃣ Please consider contacting the National Eating Disorders Association Helpline at 1-800-931-2237 for immediate support\n"
            "2️⃣ Speak with a healthcare provider as soon as possible, as eating disorders can cause serious medical complications\n"
            "3️⃣ Remember that struggling with an eating disorder isn't a choice or moral failing – these are complex conditions requiring professional treatment\n\n"
            "👨‍⚕️ Dr. David Kim specializes in eating disorder recovery and offers urgent assessments. "
            "🌟 Many people fully recover from eating disorders with comprehensive treatment."
        )
    },
    "self_harm": {
        "positive": (
            "🌱 I appreciate your openness about these difficult thoughts. Building on your existing coping strategies, consider:\n\n"
            "1️⃣ Creating a detailed safety plan with specific actions for different distress levels\n"
            "2️⃣ Expanding your emotional vocabulary to better identify and express feelings\n"
            "3️⃣ Working with a therapist on addressing underlying needs and emotions\n\n"
            "📱 The SafeSpot app offers privacy-protected tracking of urges and healthy coping alternatives. "
            "👩‍⚕️ Dr. Rebecca Martinez specializes in self-harm recovery and can provide evidence-based approaches like Dialectical Behavior Therapy."
        ),
        "neutral": (
            "🧠 Self-harm thoughts deserve compassionate attention and care. Some helpful approaches include:\n\n"
            "1️⃣ Creating distance between urges and actions using strategies like 'urge surfing'\n"
            "2️⃣ Developing a toolkit of alternative coping strategies for different emotions (ice cubes for anger, soft blankets for sadness, etc.)\n"
            "3️⃣ Practicing mindfulness to increase awareness of emotional triggers\n"
            "4️⃣ Building a support network of people you can reach out to when urges arise\n\n"
            "👨‍⚕️ Dr. Michael Wei specializes in self-harm treatment and offers evidence-based approaches like Emotion Regulation Therapy."
        ),
        "negative": (
            "💜 I'm deeply concerned about your self-harm thoughts and want to ensure your safety. "
            "For immediate support:\n\n"
            "1️⃣ Please contact the Crisis Text Line by texting HOME to 741741 or call the National Suicide Prevention Lifeline at 988\n"
            "2️⃣ Remove access to items that could be used for self-harm if possible\n"
            "3️⃣ Use strong sensory experiences like holding ice cubes or snapping a rubber band as temporary alternatives\n"
            "4️⃣ Reach out to a trusted person who can stay with you until the intense urges pass\n\n"
            "👩‍⚕️ Dr. Samantha Park specializes in crisis intervention and can provide immediate and ongoing support. "
            "✨ Many people who have struggled with self-harm develop effective coping skills with proper support."
        )
    },
    "suicide": {
        "default": (
            "❗ I'm deeply concerned about you right now. If you're having thoughts of suicide, please know that immediate help is available. "
            "Please contact the National Suicide Prevention Lifeline at 988 (call or text) or chat at 988lifeline.org.\n\n"
            "These trained counselors are available 24/7 to provide support during this difficult time. "
            "If you're in immediate danger, please call 911 or go to your nearest emergency room.\n\n"
            "💙 Your life matters, and there are dedicated professionals who can help you through this crisis. "
            "Many people who have experienced suicidal thoughts have found relief and gone on to live fulfilling lives with proper support.\n\n"
            "👨‍⚕️ Dr. James Wilson specializes in suicide prevention and crisis management."
        )
    },
    "substance_abuse": {
        "positive": (
            "🌱 I appreciate your awareness about substance use concerns. "
            "To continue making positive changes:\n\n"
            "1️⃣ Track specific situations, emotions, and thoughts that precede substance use\n"
            "2️⃣ Expand your toolkit of alternative coping strategies for each trigger\n"
            "3️⃣ Consider both professional support and peer recovery communities\n\n"
            "🧠 The SMART Recovery program offers science-based tools for managing addictive behaviors. "
            "👨‍⚕️ Dr. Thomas Chen specializes in substance use treatment and can discuss various approaches, including medication options if appropriate."
        ),
        "neutral": (
            "⚖️ Concerns about substance use deserve thoughtful attention. Some helpful approaches include:\n\n"
            "1️⃣ Honestly assessing how substance use affects your relationships, work, health, and goals\n"
            "2️⃣ Speaking with a healthcare provider about safe options if physical dependence is a concern\n"
            "3️⃣ Exploring both professional treatment and peer support groups like SMART Recovery or 12-step programs\n"
            "4️⃣ Developing healthy coping skills for stress and difficult emotions\n\n"
            "📞 The Substance Abuse and Mental Health Services Administration (SAMHSA) offers a 24/7 helpline at 1-800-662-HELP. "
            "👩‍⚕️ Dr. Maria Rodriguez specializes in addiction medicine and can help determine the best approach for your situation."
        ),
        "negative": (
            "💙 I'm concerned about your struggles with substances and want you to know that help is available. "
            "For immediate support:\n\n"
            "1️⃣ Please consider contacting SAMHSA's National Helpline at 1-800-662-HELP, which provides free, confidential, 24/7 information and referrals\n"
            "2️⃣ If you're experiencing withdrawal symptoms, seek medical attention as some withdrawals can be dangerous\n"
            "3️⃣ Know that addiction is a medical condition, not a moral failing, and effective treatments are available\n\n"
            "👨‍⚕️ Dr. Robert Park specializes in addiction medicine and offers compassionate care, including medication-assisted treatment when appropriate. "
            "✨ Many people achieve long-term recovery with proper support."
        )
    },
    "bipolar": {
    "positive": (
        "🌈 I appreciate your awareness about bipolar symptoms. "
        "To maintain stability:\n\n"
        "1️⃣ Continue tracking mood patterns daily, which helps identify early warning signs of episodes\n"
        "2️⃣ Maintain extremely regular sleep patterns, as sleep disruption can trigger episodes\n"
        "3️⃣ Work with your provider on a specific plan for what to do if you notice warning signs of mania or depression\n\n"
        "📱 The app eMoods can help track mood, sleep, medication, and other factors. "
        "👩‍⚕️ Dr. Elizabeth Chen specializes in bipolar disorder management and can provide comprehensive care."
    ),
    "neutral": (
        "⚖️ Bipolar disorder is a manageable condition with proper treatment. Some helpful approaches include:\n\n"
        "1️⃣ Working with a psychiatrist experienced in bipolar disorder, as medication is usually an essential component of treatment\n"
        "2️⃣ Establishing very regular routines for sleep, meals, and exercise\n"
        "3️⃣ Learning to identify your unique early warning signs of mood episodes\n"
        "4️⃣ Building a support network that understands bipolar disorder\n\n"
        "🤝 The Depression and Bipolar Support Alliance offers peer support groups that many find helpful. "
        "👨‍⚕️ Dr. Michael Thompson specializes in bipolar disorder treatment and offers evidence-based approaches."
    ),
    "negative": (
        "💙 I'm concerned about your bipolar symptoms and want you to know that effective help is available. "
        "For immediate support:\n\n"
        "1️⃣ If you're experiencing thoughts of harming yourself, please contact the National Suicide Prevention Lifeline at 988\n"
        "2️⃣ Contact your healthcare provider or go to the emergency room if you're experiencing severe symptoms, as rapid treatment can prevent full episodes\n"
        "3️⃣ Know that medication adjustment may be needed, and this is a normal part of bipolar management\n\n"
        "👩‍⚕️ Dr. Sarah Williams specializes in bipolar disorder treatment and offers urgent appointments for symptom management. "
        "✨ With proper treatment, many people with bipolar disorder lead stable, fulfilling lives."
    )
    },
    "schizophrenia": {
    "positive": (
        "🌟 I appreciate your insight into your experiences. "
        "To support your continued wellness:\n\n"
        "1️⃣ Continue working closely with your treatment team\n"
        "2️⃣ Consider using technology like medication reminder apps to support treatment adherence\n"
        "3️⃣ Participate in cognitive enhancement programs like Cognitive Remediation Therapy, which can improve cognition and daily functioning\n\n"
        "🗣️ The LEAP (Listen-Empathize-Agree-Partner) approach can help family members provide effective support. "
        "👨‍⚕️ Dr. James Chen specializes in schizophrenia spectrum disorders and offers evidence-based treatment approaches."
    ),
    "neutral": (
        "⚖️ Schizophrenia is a complex but treatable condition. Some helpful approaches include:\n\n"
        "1️⃣ Working with a psychiatrist experienced in psychotic disorders, as medication is a crucial component of treatment\n"
        "2️⃣ Developing a clear plan for what to do if symptoms increase\n"
        "3️⃣ Establishing regular routines for sleep, meals, and activities\n"
        "4️⃣ Connecting with others through organizations like Schizophrenia and Related Disorders Alliance of America\n\n"
        "🧠 Cognitive Behavioral Therapy for psychosis (CBTp) can help manage persistent symptoms. "
        "👩‍⚕️ Dr. Rebecca Park specializes in schizophrenia treatment and offers comprehensive care."
    ),
    "negative": (
        "💙 I'm concerned about your experiences and want you to know that effective help is available. "
        "For immediate support:\n\n"
        "1️⃣ Please consider contacting the SAMHSA Helpline at 1-800-662-HELP for treatment referrals\n"
        "2️⃣ If you're experiencing a crisis, the Crisis Text Line (text HOME to 741741) can provide immediate support\n"
        "3️⃣ Know that with proper treatment, symptoms can significantly improve and many people with schizophrenia lead fulfilling lives\n\n"
        "🏥 Early Psychosis Intervention Centers offer specialized treatment for early psychosis. "
        "👨‍⚕️ Dr. Michael Lee specializes in schizophrenia spectrum disorders and provides evidence-based, compassionate care."
    )
},
"ocd": {
    "positive": (
        "🌱 I appreciate your awareness about OCD symptoms. "
        "To build on your progress:\n\n"
        "1️⃣ Continue practicing Exposure and Response Prevention exercises, gradually increasing difficulty\n"
        "2️⃣ Apply mindfulness techniques specifically for OCD (like accepting intrusive thoughts without engaging with them)\n"
        "3️⃣ Work with a therapist to identify and challenge OCD-related beliefs\n\n"
        "📚 The book 'Freedom from OCD' by Jonathan Grayson offers self-directed ERP exercises. "
        "👩‍⚕️ Dr. Sarah Thompson specializes in OCD treatment and can provide specialized care."
    ),
    "neutral": (
        "⚖️ OCD is a challenging but treatable condition. Some helpful approaches include:\n\n"
        "1️⃣ Learning about Exposure and Response Prevention (ERP) therapy, the gold standard treatment for OCD\n"
        "2️⃣ Working with a therapist trained specifically in OCD treatment\n"
        "3️⃣ Understanding that seeking certainty fuels OCD cycles\n"
        "4️⃣ Joining an OCD support group to connect with others who understand\n\n"
        "🔍 The International OCD Foundation offers resources and provider listings at iocdf.org. "
        "👨‍⚕️ Dr. David Wilson specializes in OCD treatment and offers evidence-based approaches."
    ),
    "negative": (
        "💙 I'm truly sorry you're struggling with such difficult OCD symptoms. "
        "For immediate support:\n\n"
        "1️⃣ Try the 'STOPP' technique when intrusive thoughts arise (Stop, Take a breath, Observe the thought without judgment, Pull back for perspective, Practice what works)\n"
        "2️⃣ Contact the International OCD Foundation's resource helpline at 617-973-5801\n"
        "3️⃣ Remember that even severe OCD can significantly improve with proper treatment\n\n"
        "👩‍⚕️ Dr. Jessica Chen specializes in severe OCD and offers intensive treatment programs when weekly therapy isn't sufficient. "
        "✨ Many people who have struggled with debilitating OCD have achieved substantial relief with effective treatment."
    )
},
"general": {
    "positive": (
        "🌈 I appreciate your thoughtful reflection on your mental health. "
        "To continue supporting your wellbeing:\n\n"
        "1️⃣ Consider maintaining a wellness journal to track activities, relationships, and practices that positively impact your mental health\n"
        "2️⃣ Explore mindfulness practices that resonate with you, such as meditation, mindful walking, or breathwork\n"
        "3️⃣ Schedule regular check-ins with yourself to assess how you're feeling and what adjustments might help\n\n"
        "📚 The book 'The Upward Spiral' by Alex Korb explains the neuroscience behind many effective mental health practices. "
        "👩‍⚕️ Dr. Jennifer Williams specializes in preventative mental healthcare and can provide additional strategies if needed."
    ),
    "neutral": (
        "⚖️ Taking care of your mental health is as important as physical health. Some helpful general approaches include:\n\n"
        "1️⃣ Establishing consistent routines for sleep, meals, and activity\n"
        "2️⃣ Practicing stress management techniques like deep breathing or progressive muscle relaxation\n"
        "3️⃣ Spending time in nature, which research shows improves mood\n"
        "4️⃣ Nurturing social connections, even brief ones\n\n"
        "🌐 The website mentalhealth.gov offers reliable information on various mental health topics. "
        "👨‍⚕️ Dr. Robert Chen provides general mental health care and can help determine if specific concerns need specialized attention."
    ),
    "negative": (
        "💙 I'm sorry you're going through such a difficult time. "
        "When overall mental health feels poor:\n\n"
        "1️⃣ Focus first on basics like sleep, nutrition, and some form of movement, however gentle\n"
        "2️⃣ Reach out to one supportive person rather than isolating yourself\n"
        "3️⃣ Consider contacting a mental health professional, as proper assessment can guide effective treatment\n"
        "4️⃣ Remember that mental health can improve with proper support and treatment\n\n"
        "📞 The SAMHSA National Helpline at 1-800-662-HELP can provide treatment referrals. "
        "👩‍⚕️ Dr. Sarah Thompson offers comprehensive mental health assessments and can help determine the best approach for your specific situation."
    )
},
"burnout": {
    "positive": (
        "🌱 I notice you're recognizing the signs of burnout while maintaining some perspective, which is valuable. "
        "To address burnout effectively:\n\n"
        "1️⃣ Identify specific energy drains in your work or life and develop boundaries around them\n"
        "2️⃣ Schedule regular periods of complete disconnection from work and responsibilities\n"
        "3️⃣ Reconnect with activities that bring you a sense of meaning and accomplishment\n\n"
        "📚 The book 'Burnout: The Secret to Unlocking the Stress Cycle' by Emily and Amelia Nagoski offers science-based recovery strategies. "
        "👩‍⚕️ Dr. Michelle Garcia specializes in burnout recovery and professional sustainability."
    ),
    "neutral": (
        "⚖️ Burnout develops gradually and requires intentional recovery. Some helpful approaches include:\n\n"
        "1️⃣ Assessing which aspects of your situation contribute most to burnout (workload, control, reward, community, fairness, or values)\n"
        "2️⃣ Creating clear boundaries between work and rest time\n"
        "3️⃣ Practicing saying 'no' to additional responsibilities when possible\n"
        "4️⃣ Reconnecting with the purpose or meaning behind your work or responsibilities\n\n"
        "⏱️ Short daily restorative practices often help more than occasional longer breaks. "
        "👨‍⚕️ Dr. James Wilson specializes in burnout recovery and can provide personalized strategies."
    ),
    "negative": (
        "💙 I'm truly sorry you're experiencing such severe burnout. When burnout reaches this level:\n\n"
        "1️⃣ Consider whether a temporary step back from some responsibilities is possible\n"
        "2️⃣ Focus on physical restoration through sleep, nutrition, and gentle movement\n"
        "3️⃣ Seek support from a healthcare provider, as burnout can impact physical health and sometimes resembles depression\n"
        "4️⃣ Remember that recovery from even severe burnout is possible with proper support and changes\n\n"
        "👩‍⚕️ Dr. Elizabeth Park specializes in severe burnout recovery and can help create a sustainable path forward. "
        "✨ Many people recover from burnout and develop more sustainable ways of working and living."
    )
},
"panic": {
    "positive": (
        "🌈 I appreciate your awareness of panic experiences. "
        "To further manage panic symptoms:\n\n"
        "1️⃣ Practice the 'Five Senses Exercise' during early warning signs (identify five things you can see, four you can touch, three you can hear, two you can smell, one you can taste)\n"
        "2️⃣ Learn diaphragmatic breathing through resources like the Breathe2Relax app\n"
        "3️⃣ Gradually expose yourself to feared sensations in safe settings (like mild exercise to experience increased heart rate without danger)\n\n"
        "👩‍⚕️ Dr. Rachel Foster specializes in panic disorder treatment and can refine your management techniques."
    ),
    "neutral": (
        "⚖️ Panic attacks are frightening but not physically dangerous. Some helpful approaches include:\n\n"
        "1️⃣ Practicing slow breathing (four counts in, hold for one, six counts out) daily so it's easier to use during panic\n"
        "2️⃣ Challenging catastrophic thoughts with reality-based alternatives\n"
        "3️⃣ Learning about the body's fight-or-flight response to understand physical symptoms\n"
        "4️⃣ Gradually facing feared situations with support\n\n"
        "🧠 Cognitive Behavioral Therapy is highly effective for panic disorder. "
        "👨‍⚕️ Dr. Thomas Lee specializes in anxiety disorders and can provide evidence-based treatment."
    ),
    "negative": (
        "💙 I'm truly sorry you're experiencing such terrifying panic symptoms. "
        "During a panic attack:\n\n"
        "1️⃣ Focus on fully exhaling - lengthening your exhale helps activate your parasympathetic nervous system\n"
        "2️⃣ Remind yourself that panic always passes and the sensations cannot harm you\n"
        "3️⃣ Ground yourself by placing your feet firmly on the floor and noticing the sensation\n"
        "4️⃣ If possible, continue normal activities during the attack rather than fleeing the situation\n\n"
        "👩‍⚕️ Dr. Sarah Williams specializes in panic disorder and can provide both immediate management techniques and effective long-term treatment. "
        "✨ Panic disorder responds very well to proper treatment, and complete recovery is possible."
    )
    },
    "trauma": {
    "positive": (
        "🌱 I appreciate your resilience in addressing trauma. "
        "To support your continued healing:\n\n"
        "1️⃣ Continue practicing grounding techniques when trauma memories arise\n"
        "2️⃣ Consider trauma-specific therapies like EMDR (Eye Movement Desensitization and Reprocessing) or CPT (Cognitive Processing Therapy)\n"
        "3️⃣ Build a 'trauma-informed' support network of people who understand trauma responses\n\n"
        "📚 The book 'The Body Keeps the Score' by Bessel van der Kolk explains trauma's impacts and evidence-based treatments. "
        "👩‍⚕️ Dr. Maria Rodriguez specializes in trauma recovery and offers various trauma-specific therapies."
    ),
    "neutral": (
        "⚖️ Trauma responses are normal reactions to abnormal events. Some helpful approaches include:\n\n"
        "1️⃣ Learning about how trauma affects the body and brain, which can make responses more understandable\n"
        "2️⃣ Practicing grounding techniques like the 5-4-3-2-1 exercise when triggered\n"
        "3️⃣ Building safety and stability in daily life before processing trauma memories\n"
        "4️⃣ Considering trauma-specific therapies when ready\n\n"
        "🌐 The National Center for PTSD offers educational resources at www.ptsd.va.gov. "
        "👨‍⚕️ Dr. William Lee specializes in trauma treatment and can provide trauma-informed care."
    ),
    "negative": (
        "💙 I'm deeply sorry for the trauma you've experienced and the pain you're feeling now. "
        "When trauma symptoms feel overwhelming:\n\n"
        "1️⃣ Focus first on establishing physical and emotional safety\n"
        "2️⃣ Use strong sensory experiences (like holding ice, smelling essential oils, or listening to music) to ground yourself in the present\n"
        "3️⃣ Remind yourself that you survived the traumatic event(s) and are now in a different time and place\n"
        "4️⃣ Consider reaching out to a trauma-informed therapist\n\n"
        "👩‍⚕️ Dr. Jessica Park specializes in complex trauma and offers trauma-sensitive approaches to healing. "
        "✨ Recovery from trauma is possible, and many people find their symptoms significantly improve with proper support."
    )
    }
}

def select_response(intent, sentiment, user_message):
    """
    Select an appropriate response based on intent and sentiment analysis.
    """
    if intent in RESPONSES:
        # Special case for suicide intent - always return the default response
        if intent == "suicide":
            return RESPONSES[intent]["default"]
        
        # For other intents with sentiment-based responses
        if intent in ["loneliness", "depression", "anxiety", "stress", "ptsd", "grief", 
                      "addiction", "relationship", "breakup", "insomnia", "eating_disorder", 
                      "self_harm", "substance_abuse", "bipolar", "schizophrenia", "ocd", 
                      "general", "burnout", "panic", "trauma"]:
            if sentiment >= 0.3:
                return RESPONSES[intent]["positive"]
            elif sentiment <= -0.3:
                return RESPONSES[intent]["negative"]
            else:
                return RESPONSES[intent]["neutral"]
    
    # If intent not found or doesn't match any specific condition, return general response
    if sentiment >= 0.3:
        return RESPONSES["general"]["positive"]
    elif sentiment <= -0.3:
        return RESPONSES["general"]["negative"]
    else:
        return RESPONSES["general"]["neutral"]

# Simple email validation using regex
def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b'
    return re.match(regex, email) is not None

# -------- Session Status Endpoint --------
@app.route('/session-status', methods=["GET"])
def session_status():
    if "email" in session:
        return jsonify({"logged_in": True, "email": session["email"]}), 200
    else:
        return jsonify({"logged_in": False}), 200

# -------- Authentication Endpoints --------
@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()

    if not name or not email or not password or not confirm_password:
        return jsonify({"message": "All fields (name, email, password, confirm password) are required."}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Please provide a valid email address."}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters long."}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "A user with this email already exists."}), 400

    new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201

@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password."}), 401

    session.permanent = True  # Mark session as permanent to use the lifetime defined above
    session["email"] = email
    session.pop("conversation", None)
    return jsonify({"message": "Login successful."}), 200

@app.route('/logout', methods=["POST"])
def logout():
    session.pop("email", None)
    session.pop("conversation", None)
    return jsonify({"message": "Logged out successfully."}), 200

# -------- Chat Endpoint (Requires Login) --------
@app.route('/chat', methods=["POST"])
def chat():
    if "email" not in session:
        return jsonify({"message": "Unauthorized. Please log in."}), 401

    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"message": "Please provide a valid message."}), 400

    intent = extract_intent(user_message)
    sentiment = analyze_sentiment(user_message)
    entities = extract_entities(user_message)

    conversation = session.get("conversation", [])
    if len(conversation) > 4:
        conversation = conversation[-4:]
    conversation.append({"user": user_message, "intent": intent, "sentiment": sentiment})
    session["conversation"] = conversation

    response_text = select_response(intent, sentiment, user_message)
    
    # Add follow-up question if appropriate
    follow_up = get_follow_up_question(intent)
    if follow_up:
        response_text += f"\n\n{follow_up}"
    
    conversation.append({"advisor": response_text})
    session["conversation"] = conversation

    return jsonify({"message": response_text})

if __name__ == '__main__':
    app.run(debug=True)