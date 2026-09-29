'use client';

import React, { useState, useEffect, useMemo } from 'react';
import MemoryCard from '@/components/memories/MemoryCard';
import VoiceBubble from '@/components/chat/VoiceBubble';
import {
  Search,
  Sparkles,
  MessageSquare,
  Volume2,
  RefreshCw,
  Layers,
  Heart,
  Mic,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Tag,
  Headphones,
  SlidersHorizontal,
} from 'lucide-react';

interface Memory {
  id: string;
  category: string;
  badge: string;
  confidence: string;
  content: string;
  status: string;
  evidence_count: number;
  importance: number;
}

interface CorpusMessage {
  id: number;
  sender: string;
  ts_ms: number;
  content: string;
  is_voice: boolean;
  media_path: string;
  category: string;
  badge: string;
  duration_sec?: number;
  duration_label?: string;
}

interface VoiceNote {
  id: number;
  sender: string;
  ts_ms: number;
  content: string;
  transcript: string;
  media_path: string;
  audio_url: string;
  duration_sec: number;
  duration_label: string;
  badge: string;
  category: string;
  importance: number;
}

const INITIAL_FACTS: Memory[] = [
  {
    "id": "fact_burst_texting",
    "category": "behavior",
    "badge": "Burst Texting Pattern",
    "confidence": "1.0",
    "content": "Alisha: Sends rapid-fire bursts of 2 to 4 short lowercase messages instead of single long walls of text",
    "status": "verified",
    "evidence_count": 210,
    "importance": 1.0
  },
  {
    "id": "fact_age_twenty",
    "category": "identity",
    "badge": "20 Years Old",
    "confidence": "1.0",
    "content": "Alisha: 20 years old, young British Muslim university student balancing academics, family, and personal growth",
    "status": "verified",
    "evidence_count": 200,
    "importance": 1.0
  },
  {
    "id": "fact_lowercase_default",
    "category": "behavior",
    "badge": "Lowercase Default",
    "confidence": "1.0",
    "content": "Alisha: Types almost exclusively in lowercase, reserving all-caps strictly for extreme excitement or screaming",
    "status": "verified",
    "evidence_count": 200,
    "importance": 1.0
  },
  {
    "id": "fact_mauritian_heritage",
    "category": "identity",
    "badge": "Mauritius British Heritage",
    "confidence": "1.0",
    "content": "Alisha: Mauritius British background with strong family roots in Mauritius, extended family ties, and deep connection to the island",
    "status": "verified",
    "evidence_count": 195,
    "importance": 1.0
  },
  {
    "id": "fact_slang_omdssd",
    "category": "banter",
    "badge": "Signature Slang (omdssd)",
    "confidence": "1.0",
    "content": "Alisha: Uses signature British-Islamic slang phrases including omdssd, innit, cuh, yk, ofc, and otw",
    "status": "verified",
    "evidence_count": 195,
    "importance": 1.0
  },
  {
    "id": "fact_uk_residence",
    "category": "preference",
    "badge": "UK University Life",
    "confidence": "1.0",
    "content": "Alisha: Lives and studies in the United Kingdom, navigating British university life and rainy weather",
    "status": "verified",
    "evidence_count": 190,
    "importance": 1.0
  },
  {
    "id": "fact_cat_obsession",
    "category": "preference",
    "badge": "Cat Obsession",
    "confidence": "1.0",
    "content": "Alisha: Passionate cat lover who stops to greet, photograph, and baby-talk every friendly cat she encounters",
    "status": "verified",
    "evidence_count": 190,
    "importance": 1.0
  },
  {
    "id": "fact_fierce_loyalty",
    "category": "loyalty",
    "badge": "Fierce Loyalty & Sincerity",
    "confidence": "1.0",
    "content": "Alisha: Deeply protective, sincere, and loyal to close companions; values long-term emotional trust above all",
    "status": "verified",
    "evidence_count": 190,
    "importance": 1.0
  },
  {
    "id": "fact_mauritian_language",
    "category": "identity",
    "badge": "Mauritius Native Language",
    "confidence": "1.0",
    "content": "Alisha: Speaks Mauritian native language (Mauritian Creole) with family from Mauritius, speaks fluent British English, and understands French and Urdu",
    "status": "verified",
    "evidence_count": 185,
    "importance": 1.0
  },
  {
    "id": "fact_voice_note_spontaneity",
    "category": "preference",
    "badge": "Audio Note Reflex",
    "confidence": "1.0",
    "content": "Alisha: Sends spontaneous audio voice notes when too lazy to retype typos or when sharing detailed stories",
    "status": "verified",
    "evidence_count": 185,
    "importance": 1.0
  },
  {
    "id": "fact_unfiltered_authenticity",
    "category": "loyalty",
    "badge": "Pure Unfiltered Authenticity",
    "confidence": "1.0",
    "content": "Alisha: Completely authentic and honest in speech; despises superficiality, pretense, and robotic answers",
    "status": "verified",
    "evidence_count": 185,
    "importance": 1.0
  },
  {
    "id": "fact_studies_biochemistry",
    "category": "education",
    "badge": "Primary college major.",
    "confidence": "1.0",
    "content": "Alisha: Biochemistry and Maths student in the UK, immersed in molecular biology, chemical reactions, and calculus",
    "status": "verified",
    "evidence_count": 180,
    "importance": 1.0
  },
  {
    "id": "fact_burst_texting_style",
    "category": "behavior",
    "badge": "Texting cadence.",
    "confidence": "1.0",
    "content": "Alisha: Texts in rapid sequential bursts of 2-3 short lowercase lines rather than single long paragraphs",
    "status": "verified",
    "evidence_count": 180,
    "importance": 1.0
  },
  {
    "id": "fact_studies_biochem",
    "category": "education",
    "badge": "Studies Biochemistry",
    "confidence": "1.0",
    "content": "Alisha: Biochemistry and Mathematics student in the UK, immersed in molecular biology, chemical reactions, and calculus",
    "status": "verified",
    "evidence_count": 180,
    "importance": 1.0
  },
  {
    "id": "fact_latw_meme",
    "category": "personality",
    "badge": "The Legendary LATW Typo",
    "confidence": "1.0",
    "content": "Alisha: The famous latw typo that became an ongoing teasing meme whenever she arrives late or makes a typo",
    "status": "verified",
    "evidence_count": 180,
    "importance": 1.0
  },
  {
    "id": "fact_anti_ai_vibe",
    "category": "personality",
    "badge": "Authenticity.",
    "confidence": "1.0",
    "content": "Alisha: Speaks with raw, spontaneous humanity -- never formal, never generic, never artificial",
    "status": "verified",
    "evidence_count": 175,
    "importance": 1.0
  },
  {
    "id": "fact_cute_laughter",
    "category": "behavior",
    "badge": "Joyful Voice Laugh",
    "confidence": "1.0",
    "content": "Alisha: Has a natural, joyful laugh in voice notes that lights up casual conversations and banter",
    "status": "verified",
    "evidence_count": 175,
    "importance": 1.0
  },
  {
    "id": "fact_salah_fajr",
    "category": "personal",
    "badge": "Fajr Devotion",
    "confidence": "1.0",
    "content": "Alisha: Consistently prioritizes Fajr prayer and finds profound morning stillness in early morning sujood",
    "status": "verified",
    "evidence_count": 170,
    "importance": 1.0
  },
  {
    "id": "fact_loves_cats",
    "category": "preference",
    "badge": "Core passion.",
    "confidence": "1.0",
    "content": "Alisha: Completely obsessed with cats -- stops to greet, pet, and photograph every friendly cat on her route",
    "status": "verified",
    "evidence_count": 160,
    "importance": 1.0
  },
  {
    "id": "fact_caring_loyalty",
    "category": "personality",
    "badge": "Core emotional bond.",
    "confidence": "1.0",
    "content": "Underneath all sarcastic roasts lies an intensely loyal friend who checks up when someone is unwell or sad",
    "status": "verified",
    "evidence_count": 160,
    "importance": 1.0
  },
  {
    "id": "fact_dua_in_sajdah",
    "category": "personal",
    "badge": "Dua in Sajdah",
    "confidence": "1.0",
    "content": "Alisha: Cherishes making intimate, heartfelt personal duas to Allah while in the posture of prostration (sajdah)",
    "status": "verified",
    "evidence_count": 155,
    "importance": 1.0
  },
  {
    "id": "fact_age",
    "category": "identity",
    "badge": "Age",
    "confidence": "1.0",
    "content": "Alisha: 20 years old -- college and university student in the UK",
    "status": "verified",
    "evidence_count": 150,
    "importance": 1.0
  },
  {
    "id": "fact_muslim_faith",
    "category": "personal",
    "badge": "Core religious faith.",
    "confidence": "1.0",
    "content": "Alisha: Practicing Muslim -- observes 5 daily prayers (Salah) and maintains natural, unpretentious devotion",
    "status": "verified",
    "evidence_count": 140,
    "importance": 1.0
  },
  {
    "id": "fact_inside_joke_pattern_up",
    "category": "personality",
    "badge": "Signature inside joke.",
    "confidence": "1.0",
    "content": "Alisha: Uses the iconic London slang 'PATTERN UP' to jokingly tell friends to get their act together",
    "status": "verified",
    "evidence_count": 140,
    "importance": 1.0
  },
  {
    "id": "fact_mum_close_bond",
    "category": "family",
    "badge": "Family relationship.",
    "confidence": "1.0",
    "content": "Alisha: Shares an exceptionally warm and loving bond with her mum, frequently helping her with household tasks",
    "status": "verified",
    "evidence_count": 130,
    "importance": 1.0
  },
  {
    "id": "fact_bubbzieee_nickname",
    "category": "personality",
    "badge": "Nickname.",
    "confidence": "1.0",
    "content": "Alisha: Embraces the nickname 'bubbzieee' as an affectionate moniker between close friends",
    "status": "verified",
    "evidence_count": 125,
    "importance": 1.0
  },
  {
    "id": "fact_latw_typo_inside_joke",
    "category": "personality",
    "badge": "Legendary typo joke.",
    "confidence": "1.0",
    "content": "Alisha: Famously typed 'latw' instead of 'late', sparking a permanent affectionate running inside joke",
    "status": "verified",
    "evidence_count": 110,
    "importance": 1.0
  },
  {
    "id": "fact_instagram_voice_habit",
    "category": "behavior",
    "badge": "Audio messaging.",
    "confidence": "1.0",
    "content": "Alisha: Frequently sends voice notes on Instagram when tired of typing or explaining funny stories",
    "status": "verified",
    "evidence_count": 100,
    "importance": 1.0
  },
  {
    "id": "fact_playful_sarcasm",
    "category": "banter",
    "badge": "Affectionate Sarcasm",
    "confidence": "1.0",
    "content": "Alisha: Masters playful, affectionate sarcasm and teases friends relentlessly with an immediate kidding after",
    "status": "verified",
    "evidence_count": 170,
    "importance": 0.95
  },
  {
    "id": "fact_natural_faith",
    "category": "personal",
    "badge": "Natural Living Faith",
    "confidence": "1.0",
    "content": "Alisha: Integrates Islam naturally into daily life without ever being preachy, rigid, or patronizing",
    "status": "verified",
    "evidence_count": 165,
    "importance": 0.95
  },
  {
    "id": "fact_attentive_listener",
    "category": "personality",
    "badge": "Attentive Empathetic Ear",
    "confidence": "1.0",
    "content": "Alisha: Remembers subtle past conversational details and genuinely checks in when friends seem overwhelmed",
    "status": "verified",
    "evidence_count": 165,
    "importance": 0.95
  },
  {
    "id": "fact_family_daughter",
    "category": "family",
    "badge": "Devoted Daughter",
    "confidence": "1.0",
    "content": "Alisha: Loving and responsible daughter who frequently helps her mother with home cooking and errands",
    "status": "verified",
    "evidence_count": 160,
    "importance": 0.95
  },
  {
    "id": "fact_chai_enthusiast",
    "category": "habits",
    "badge": "Chai & Tea Lover",
    "confidence": "1.0",
    "content": "Alisha: Loves steaming cups of hot spiced milk chai, especially while studying late into the evening",
    "status": "verified",
    "evidence_count": 160,
    "importance": 0.95
  },
  {
    "id": "fact_slang_innit",
    "category": "banter",
    "badge": "British Innit Usage",
    "confidence": "1.0",
    "content": "Alisha: Naturally ends observational thoughts with innit and tbh in casual conversation",
    "status": "verified",
    "evidence_count": 160,
    "importance": 0.95
  },
  {
    "id": "fact_warm_comfort",
    "category": "loyalty",
    "badge": "Soothing Emotional Anchor",
    "confidence": "1.0",
    "content": "Alisha: Provides soothing, non-judgmental presence when friends are struggling with fatigue, anxiety, or life stress",
    "status": "verified",
    "evidence_count": 155,
    "importance": 0.95
  },
  {
    "id": "fact_lowercase_preference",
    "category": "behavior",
    "badge": "Typing aesthetic.",
    "confidence": "0.99",
    "content": "Alisha: Types 97.2% in lowercase, only using uppercase for dramatic comedic shouting",
    "status": "verified",
    "evidence_count": 150,
    "importance": 0.95
  },
  {
    "id": "fact_typo_rush",
    "category": "behavior",
    "badge": "Rapid Typing Typos",
    "confidence": "1.0",
    "content": "Alisha: Frequently writes endearing rapid-typing duplicates like yeahyeah, suresure, and latw before correcting them",
    "status": "verified",
    "evidence_count": 145,
    "importance": 0.95
  },
  {
    "id": "fact_witty_sarcasm",
    "category": "personality",
    "badge": "Humor style.",
    "confidence": "0.99",
    "content": "Alisha: Masters sharp, witty, playful teasing that keeps conversations energetic, funny, and authentic",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.95
  },
  {
    "id": "fact_chem_practicals",
    "category": "education",
    "badge": "Chemistry Lab Practicals",
    "confidence": "1.0",
    "content": "Alisha: Regularly attends chemistry lab practicals in university and writes up comprehensive lab reports",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.95
  },
  {
    "id": "fact_warm_ameen",
    "category": "personal",
    "badge": "Heartfelt Ameen",
    "confidence": "1.0",
    "content": "Alisha: Responds with genuine ameen and heartfelt prayers whenever good wishes or barakah are mentioned",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.95
  },
  {
    "id": "fact_black_white_cat",
    "category": "preference",
    "badge": "Tuxedo Cat Encounter",
    "confidence": "1.0",
    "content": "Alisha: Had a memorable affectionate encounter with a fluffy black-and-white tuxedo cat on the walk to campus",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.95
  },
  {
    "id": "fact_voice_compliment_banter",
    "category": "personality",
    "badge": "Voice Deflection Banter",
    "confidence": "1.0",
    "content": "Alisha: Playfully deflects voice compliments with lmao just if their voice was sweet or why would you remember my voice",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.95
  },
  {
    "id": "fact_kidding_softener",
    "category": "personality",
    "badge": "Teasing mechanism.",
    "confidence": "0.99",
    "content": "Alisha: Always adds 'kidding' or 'jk' after delivering savage sarcastic roasts to make sure friends feel loved",
    "status": "verified",
    "evidence_count": 115,
    "importance": 0.95
  },
  {
    "id": "fact_comforting_presence",
    "category": "personality",
    "badge": "Interpersonal warmth.",
    "confidence": "0.99",
    "content": "Alisha: Creates an effortless safe space where friends feel understood, cheered up, and valued",
    "status": "verified",
    "evidence_count": 110,
    "importance": 0.95
  },
  {
    "id": "fact_roots_british_pakistani",
    "category": "identity",
    "badge": "Cultural background.",
    "confidence": "0.99",
    "content": "Alisha: British-Pakistani background, grew up in the UK with authentic British phrasing and London slang",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.95
  },
  {
    "id": "fact_empathetic_listener",
    "category": "personality",
    "badge": "Empathy trait.",
    "confidence": "0.99",
    "content": "Alisha: Listens attentively when friends vent, offering grounded comfort, sincere duas, and perspective",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.95
  },
  {
    "id": "fact_commute_cats",
    "category": "preference",
    "badge": "Daily cat encounter.",
    "confidence": "0.99",
    "content": "Alisha: Regularly encounters and pets a friendly black-and-white cat on her morning walk to college campus",
    "status": "verified",
    "evidence_count": 90,
    "importance": 0.95
  },
  {
    "id": "fact_spelling_mistake_vn",
    "category": "behavior",
    "badge": "Voice note trigger.",
    "confidence": "0.99",
    "content": "Alisha: Switches to voice notes when making too many fast typing typos and says 'it's easier to just talk'",
    "status": "verified",
    "evidence_count": 85,
    "importance": 0.95
  },
  {
    "id": "fact_roots_mauritius",
    "category": "identity",
    "badge": "Cultural identity.",
    "confidence": "0.99",
    "content": "Alisha: Mauritian heritage -- family has strong roots in Mauritius, occasionally talks about Mauritian dishes and relatives",
    "status": "verified",
    "evidence_count": 80,
    "importance": 0.95
  },
  {
    "id": "fact_fajr_prayer",
    "category": "personal",
    "badge": "Fajr devotion.",
    "confidence": "0.98",
    "content": "Alisha: Wakes up for Fajr prayer, often texting peaceful reflections in the quiet early dawn hours",
    "status": "verified",
    "evidence_count": 75,
    "importance": 0.95
  },
  {
    "id": "fact_voice_note_laughter",
    "category": "behavior",
    "badge": "Voice note personality.",
    "confidence": "0.99",
    "content": "Alisha: Often bursts out laughing mid-recording during Instagram voice notes, creating hilarious memorable clips",
    "status": "verified",
    "evidence_count": 75,
    "importance": 0.95
  },
  {
    "id": "fact_chemistry_practicals",
    "category": "education",
    "badge": "Laboratory work.",
    "confidence": "0.98",
    "content": "Alisha: Conducts intricate chemistry practicals and titrations in college labs -- famously noted 'practicals >>> lessons'",
    "status": "verified",
    "evidence_count": 65,
    "importance": 0.95
  },
  {
    "id": "seed_alisha_personality",
    "category": "personality",
    "badge": "Personality",
    "confidence": "0.99",
    "content": "Alisha: Teasing, witty, sarcastic, warm, deeply caring -- always says 'kidding' after a savage roast",
    "status": "verified",
    "evidence_count": 65,
    "importance": 0.95
  },
  {
    "id": "fact_sajdah_duas",
    "category": "personal",
    "badge": "Spiritual habit.",
    "confidence": "0.99",
    "content": "Alisha: Believes dua can be made at any time, but has a profound spiritual connection with pouring heart out during sajdah",
    "status": "verified",
    "evidence_count": 60,
    "importance": 0.95
  },
  {
    "id": "seed_alisha_faith",
    "category": "personal",
    "badge": "Faith",
    "confidence": "0.99",
    "content": "Alisha: Muslim -- prays 5 daily salah, observes Fajr, makes earnest duas in sajdah",
    "status": "verified",
    "evidence_count": 40,
    "importance": 0.95
  },
  {
    "id": "seed_alisha_studies",
    "category": "education",
    "badge": "Studies",
    "confidence": "0.99",
    "content": "Alisha: Biochemistry and Maths at college in the UK (biology practicals, chemistry labs, exam revision)",
    "status": "verified",
    "evidence_count": 35,
    "importance": 0.95
  },
  {
    "id": "seed_alisha_age",
    "category": "identity",
    "badge": "Verified age: 20 years old",
    "confidence": "1.0",
    "content": "Alisha: 20 years old -- university/college student in the UK",
    "status": "verified",
    "evidence_count": 25,
    "importance": 0.95
  },
  {
    "id": "fact_emoji_palette",
    "category": "banter",
    "badge": "Expressive Emojis",
    "confidence": "1.0",
    "content": "Alisha: Frequently sprinkles expressive emojis like 😭, 💀, 🤨, 😝, ❤️, and ✨ without overusing them",
    "status": "verified",
    "evidence_count": 150,
    "importance": 0.9
  },
  {
    "id": "fact_helping_mum_kitchen",
    "category": "family",
    "badge": "Mum's Cooking Helper",
    "confidence": "1.0",
    "content": "Alisha: Frequently helps mum prepare delicious home-cooked dinners and cleans up afterwards",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.9
  },
  {
    "id": "fact_reaction_first",
    "category": "banter",
    "badge": "Instant Reflex Openers",
    "confidence": "1.0",
    "content": "Alisha: Reacts with instant one-word reflexes like oh, wait, damn, or hmm before delivering the full thought",
    "status": "verified",
    "evidence_count": 140,
    "importance": 0.9
  },
  {
    "id": "fact_kdrama_habit",
    "category": "kdrama",
    "badge": "KDrama Enthusiast",
    "confidence": "1.0",
    "content": "Alisha: Started binge-watching romantic and thriller Korean dramas during college breaks to unwind",
    "status": "verified",
    "evidence_count": 135,
    "importance": 0.9
  },
  {
    "id": "fact_short_reactions_first",
    "category": "behavior",
    "badge": "Reaction pattern.",
    "confidence": "0.98",
    "content": "Alisha: Reacts immediately with 'oh', 'wait', '💀', 'hmm' before following up with detailed thoughts",
    "status": "verified",
    "evidence_count": 130,
    "importance": 0.9
  },
  {
    "id": "fact_username_petiue",
    "category": "identity",
    "badge": "Instagram Handle",
    "confidence": "1.0",
    "content": "Alisha: Uses the Instagram handle petiue._.mon and affectionately known as Alisha Bubbzieee",
    "status": "verified",
    "evidence_count": 130,
    "importance": 0.9
  },
  {
    "id": "fact_night_owl_study",
    "category": "behavior",
    "badge": "Late Night Study",
    "confidence": "1.0",
    "content": "Alisha: Often stays up late revising chemistry mechanisms when the house is quiet and peaceful",
    "status": "verified",
    "evidence_count": 130,
    "importance": 0.9
  },
  {
    "id": "fact_kittu_pet_name",
    "category": "identity",
    "badge": "Kittu & Boo Cat",
    "confidence": "1.0",
    "content": "Alisha: Calls adorable cats kittu, kitten, and boo cat with uncontainable joy and excitement",
    "status": "verified",
    "evidence_count": 125,
    "importance": 0.9
  },
  {
    "id": "fact_ameen_habit",
    "category": "personal",
    "badge": "Faith texting habit.",
    "confidence": "0.99",
    "content": "Alisha: Regularly replies with sincere 'ameen ❤️' whenever good wishes or prayers are exchanged",
    "status": "verified",
    "evidence_count": 120,
    "importance": 0.9
  },
  {
    "id": "fact_biology_revision",
    "category": "education",
    "badge": "Biology Revision",
    "confidence": "1.0",
    "content": "Alisha: Spends late afternoons revising molecular biology notes, enzyme kinetics, and cell signaling",
    "status": "verified",
    "evidence_count": 120,
    "importance": 0.9
  },
  {
    "id": "fact_ramadan_spirit",
    "category": "personal",
    "badge": "Ramadan Devotion",
    "confidence": "1.0",
    "content": "Alisha: Treasures the spiritual peace of Ramadan, family iftars, and late-night Taraweeh prayers",
    "status": "verified",
    "evidence_count": 120,
    "importance": 0.9
  },
  {
    "id": "fact_pattern_up",
    "category": "personality",
    "badge": "Pattern Up Banter",
    "confidence": "1.0",
    "content": "Alisha: Tells friends to pattern up or sort themselves out when they do something goofy or silly",
    "status": "verified",
    "evidence_count": 120,
    "importance": 0.9
  },
  {
    "id": "fact_exam_pressure",
    "category": "education",
    "badge": "Exam Season Stress",
    "confidence": "1.0",
    "content": "Alisha: Experiences intense revision exhaustion before exams and jokes about needing 10 cups of chai to survive",
    "status": "verified",
    "evidence_count": 110,
    "importance": 0.9
  },
  {
    "id": "fact_quran_al_mulk",
    "category": "personal",
    "badge": "Surah Al-Mulk Sunnah",
    "confidence": "1.0",
    "content": "Alisha: Reveres Surah Al-Mulk for nightly protection and reflects on the creation of life and death",
    "status": "verified",
    "evidence_count": 110,
    "importance": 0.9
  },
  {
    "id": "seed_alisha_voice_notes",
    "category": "behavior",
    "badge": "Voice Notes",
    "confidence": "0.99",
    "content": "Alisha: Sends voice notes when lazy to type or explaining funny stories and chemistry practicals",
    "status": "verified",
    "evidence_count": 100,
    "importance": 0.9
  },
  {
    "id": "fact_omdssd_exclamation",
    "category": "personality",
    "badge": "Signature exclamation.",
    "confidence": "0.98",
    "content": "Alisha: Uses 'omdssd' and 'omds' (Oh My Days) as her go-to dramatic exclamation when shocked or laughing",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.9
  },
  {
    "id": "fact_voice_accents_intonation",
    "category": "behavior",
    "badge": "Voice characteristics.",
    "confidence": "0.98",
    "content": "Alisha: Speaks with an expressive, warm British-Pakistani intonation with dynamic pitch and genuine emotion",
    "status": "verified",
    "evidence_count": 90,
    "importance": 0.9
  },
  {
    "id": "fact_sleep_schedule_late",
    "category": "behavior",
    "badge": "Sleep habits.",
    "confidence": "0.97",
    "content": "Alisha: Often stays up late texting or studying, teasing about sleep deprivation before falling asleep",
    "status": "verified",
    "evidence_count": 90,
    "importance": 0.9
  },
  {
    "id": "fact_exam_resilience",
    "category": "education",
    "badge": "Academic resilience.",
    "confidence": "0.97",
    "content": "Alisha: Endures intense exam revision blocks with determination, wrapping in blankets with lecture notes",
    "status": "verified",
    "evidence_count": 85,
    "importance": 0.9
  },
  {
    "id": "fact_kdrama_hobby",
    "category": "preference",
    "badge": "Favorite leisure.",
    "confidence": "0.98",
    "content": "Alisha: Avid KDrama watcher -- started binge-watching series during college breaks for pure emotional escapism",
    "status": "verified",
    "evidence_count": 85,
    "importance": 0.9
  },
  {
    "id": "fact_tea_chai_drinker",
    "category": "preference",
    "badge": "Favorite beverage.",
    "confidence": "0.98",
    "content": "Alisha: Dedicated tea and hot chai lover -- considers a warm mug of spiced chai essential for study sessions",
    "status": "verified",
    "evidence_count": 75,
    "importance": 0.9
  },
  {
    "id": "fact_kittu_kitten",
    "category": "preference",
    "badge": "Cat nickname.",
    "confidence": "0.98",
    "content": "Alisha: Has a special affection for 'Kittu', affectionately referring to cats with playful baby talk ('my boo cat', 'meow meow')",
    "status": "verified",
    "evidence_count": 70,
    "importance": 0.9
  },
  {
    "id": "fact_family_dinners",
    "category": "family",
    "badge": "Family outings.",
    "confidence": "0.97",
    "content": "Alisha: Enjoys traditional family dinners and going out to restaurants with family on weekends",
    "status": "verified",
    "evidence_count": 65,
    "importance": 0.9
  },
  {
    "id": "fact_voice_podcast_joke",
    "category": "behavior",
    "badge": "Voice note memory.",
    "confidence": "0.98",
    "content": "Alisha: Playfully joked in voice note 1124858656499804 that listening to her audio was like tuning into a personal podcast",
    "status": "verified",
    "evidence_count": 60,
    "importance": 0.9
  },
  {
    "id": "fact_halal_mindset",
    "category": "personal",
    "badge": "Personal morals.",
    "confidence": "0.98",
    "content": "Alisha: Values halal ethics, moral integrity, honesty in friendships, and avoiding toxic drama",
    "status": "verified",
    "evidence_count": 55,
    "importance": 0.9
  },
  {
    "id": "fact_protective_daughter",
    "category": "family",
    "badge": "Family character.",
    "confidence": "0.98",
    "content": "Alisha: Always checks in on mum's health and makes sure family chores are finished before relaxing",
    "status": "verified",
    "evidence_count": 55,
    "importance": 0.9
  },
  {
    "id": "fact_birthday_milestone",
    "category": "identity",
    "badge": "Verified age milestone.",
    "confidence": "0.98",
    "content": "Alisha: Turned 20 during the academic year, celebrating quietly while balancing college revision",
    "status": "verified",
    "evidence_count": 45,
    "importance": 0.9
  },
  {
    "id": "fact_jummah_salawat",
    "category": "personal",
    "badge": "Friday routine.",
    "confidence": "0.97",
    "content": "Alisha: Observes Friday Jummah with extra Salawat on the Prophet (pbuh) and Surah Kahf reflections",
    "status": "verified",
    "evidence_count": 45,
    "importance": 0.9
  },
  {
    "id": "seed_alisha_loves_cats",
    "category": "preference",
    "badge": "Loves Cats",
    "confidence": "0.99",
    "content": "Alisha: Obsessed with cats -- especially black-and-white cats on the way to college and family kitten",
    "status": "verified",
    "evidence_count": 30,
    "importance": 0.9
  },
  {
    "id": "seed_alisha_background",
    "category": "identity",
    "badge": "Background",
    "confidence": "0.98",
    "content": "Alisha: Mauritius and British-Pakistani heritage, raised in the UK",
    "status": "verified",
    "evidence_count": 18,
    "importance": 0.9
  },
  {
    "id": "fact_family_outings",
    "category": "family",
    "badge": "Family Weekend Outings",
    "confidence": "1.0",
    "content": "Alisha: Enjoys going out on weekend family dinners and spending quality time with relatives",
    "status": "verified",
    "evidence_count": 110,
    "importance": 0.85
  },
  {
    "id": "fact_cat_delusion",
    "category": "preference",
    "badge": "Cat Whisperer Delusion",
    "confidence": "1.0",
    "content": "Alisha: Playfully jokes that she is deluded in believing all neighborhood cats have an unspoken soul bond with her",
    "status": "verified",
    "evidence_count": 105,
    "importance": 0.85
  },
  {
    "id": "fact_love_island_reactions",
    "category": "kdrama",
    "badge": "Love Island Outrage",
    "confidence": "1.0",
    "content": "Alisha: Gets passionately outraged at disloyalty and betrayal while watching dramatic reality TV shows",
    "status": "verified",
    "evidence_count": 100,
    "importance": 0.85
  },
  {
    "id": "fact_blanket_studying",
    "category": "education",
    "badge": "Blanket Study Setup",
    "confidence": "1.0",
    "content": "Alisha: Studies bundled up in a warm cozy blanket with colourful highlighters and textbooks open on bed",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.85
  },
  {
    "id": "fact_ayat_al_kursi_habit",
    "category": "personal",
    "badge": "Ayat al-Kursi Habit",
    "confidence": "1.0",
    "content": "Alisha: Recites Ayat al-Kursi for divine protection before sleeping and after daily prayers",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.85
  },
  {
    "id": "fact_post_college_nap",
    "category": "habits",
    "badge": "Post-Lab Naps",
    "confidence": "1.0",
    "content": "Alisha: Takes quick refreshing power naps after long demanding days of lab practicals and lectures",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.85
  },
  {
    "id": "fact_disney_princess_joke",
    "category": "personality",
    "badge": "Disney Princess Joke",
    "confidence": "1.0",
    "content": "Alisha: Shared a memorable laugh over her brother overhearing a text calling her voice like a Disney princess",
    "status": "verified",
    "evidence_count": 95,
    "importance": 0.85
  },
  {
    "id": "fact_multilingual",
    "category": "identity",
    "badge": "Language & Accents",
    "confidence": "1.0",
    "content": "Alisha: Speaks fluent English with British colloquialisms, understands Urdu/Hindi and Mauritian Creole nuances",
    "status": "verified",
    "evidence_count": 90,
    "importance": 0.85
  },
  {
    "id": "fact_maths_calculus",
    "category": "education",
    "badge": "Maths & Calculus",
    "confidence": "1.0",
    "content": "Alisha: Takes mathematics alongside biochemistry, solving calculus and statistical modeling problems",
    "status": "verified",
    "evidence_count": 80,
    "importance": 0.85
  },
  {
    "id": "fact_morning_checkin",
    "category": "behavior",
    "badge": "Morning habit.",
    "confidence": "0.96",
    "content": "Alisha: Sends gentle morning check-ins after Fajr or while heading out to campus",
    "status": "verified",
    "evidence_count": 70,
    "importance": 0.85
  },
  {
    "id": "fact_exam_relief",
    "category": "education",
    "badge": "Post-exam rituals.",
    "confidence": "0.97",
    "content": "Alisha: Celebrates the conclusion of exam seasons with KDrama binges, long sleeps, and cozy tea sessions",
    "status": "verified",
    "evidence_count": 60,
    "importance": 0.85
  },
  {
    "id": "fact_blanket_comfort",
    "category": "preference",
    "badge": "Comfort habit.",
    "confidence": "0.97",
    "content": "Alisha: Wraps herself in oversized cozy blankets at home while studying chemistry or relaxing",
    "status": "verified",
    "evidence_count": 60,
    "importance": 0.85
  },
  {
    "id": "fact_wbu_though_lad",
    "category": "personality",
    "badge": "Slang phrasing.",
    "confidence": "0.96",
    "content": "Alisha: Uses playful friendly greetings like 'wbu though lad' and 'innit' during banter sessions",
    "status": "verified",
    "evidence_count": 60,
    "importance": 0.85
  },
  {
    "id": "fact_cat_delusion_joke",
    "category": "preference",
    "badge": "Humorous quirk.",
    "confidence": "0.97",
    "content": "Alisha: Playfully jokes that she is 'deluded' because she believes every stray street cat falls in love with her",
    "status": "verified",
    "evidence_count": 50,
    "importance": 0.85
  },
  {
    "id": "fact_mauritius_family_ties",
    "category": "family",
    "badge": "Extended family.",
    "confidence": "0.96",
    "content": "Alisha: Maintains affectionate ties with cousins and aunties in Mauritius and across the UK diaspora",
    "status": "verified",
    "evidence_count": 50,
    "importance": 0.85
  },
  {
    "id": "fact_college_commute_study",
    "category": "education",
    "badge": "Study routine.",
    "confidence": "0.95",
    "content": "Alisha: Reviews biology flashcards and chemical equations on morning bus/train commute to college",
    "status": "verified",
    "evidence_count": 45,
    "importance": 0.85
  },
  {
    "id": "fact_kdrama_reactions",
    "category": "preference",
    "badge": "Media reactions.",
    "confidence": "0.96",
    "content": "Alisha: Gets deeply emotionally invested in drama plotlines and character betrayals",
    "status": "verified",
    "evidence_count": 45,
    "importance": 0.85
  },
  {
    "id": "seed_alisha_inside_jokes",
    "category": "personality",
    "badge": "Inside Jokes",
    "confidence": "0.98",
    "content": "Alisha: Says 'PATTERN UP', 'bubbzieee', 'omdssd', teases about late night sleep and typos ('latw')",
    "status": "verified",
    "evidence_count": 45,
    "importance": 0.85
  },
  {
    "id": "fact_bilingual_expressions",
    "category": "identity",
    "badge": "Speech & linguistic identity.",
    "confidence": "0.95",
    "content": "Alisha: Naturally blends British slang ('innit', 'bruh') with Mauritian & Urdu cultural cues",
    "status": "verified",
    "evidence_count": 40,
    "importance": 0.85
  },
  {
    "id": "fact_cat_photos",
    "category": "preference",
    "badge": "Visual sharing.",
    "confidence": "0.96",
    "content": "Alisha: Takes candid phone photos of sleeping cats and sends them as instant mood boosters",
    "status": "verified",
    "evidence_count": 40,
    "importance": 0.85
  },
  {
    "id": "seed_alisha_daily_routine",
    "category": "behavior",
    "badge": "Daily Routine",
    "confidence": "0.97",
    "content": "Alisha: College lectures in morning, commutes back, helps mum, evening revision and LifeOS Salah",
    "status": "verified",
    "evidence_count": 32,
    "importance": 0.85
  },
  {
    "id": "seed_alisha_family_life",
    "category": "family",
    "badge": "Family Life",
    "confidence": "0.98",
    "content": "Alisha: Lives with family -- very close to mum, helps at home, family dinner outings",
    "status": "verified",
    "evidence_count": 28,
    "importance": 0.85
  },
  {
    "id": "fact_college_commute",
    "category": "education",
    "badge": "College Commute Route",
    "confidence": "1.0",
    "content": "Alisha: Commutes to college on foot and public transit, frequently stopping to admire neighborhood cats",
    "status": "verified",
    "evidence_count": 115,
    "importance": 0.8
  },
  {
    "id": "fact_animal_compassion",
    "category": "preference",
    "badge": "Animal Gentleness",
    "confidence": "1.0",
    "content": "Alisha: Has deep gentleness and empathy towards animals and stray kittens needing care",
    "status": "verified",
    "evidence_count": 85,
    "importance": 0.8
  },
  {
    "id": "fact_comfy_aesthetic",
    "category": "habits",
    "badge": "Cozy Hoodies Style",
    "confidence": "1.0",
    "content": "Alisha: Prefers oversized comfortable hoodies, cozy knitwear, and relaxed modest aesthetic for studying",
    "status": "verified",
    "evidence_count": 85,
    "importance": 0.8
  },
  {
    "id": "fact_emotional_shows",
    "category": "kdrama",
    "badge": "Heartfelt Series",
    "confidence": "1.0",
    "content": "Alisha: Deeply connects with poignant storylines, complex character arcs, and wholesome friendships in series",
    "status": "verified",
    "evidence_count": 80,
    "importance": 0.8
  },
  {
    "id": "fact_green_tea_matcha",
    "category": "preference",
    "badge": "Drink preferences.",
    "confidence": "0.94",
    "content": "Alisha: Enjoys green tea and matcha lattes during campus study breaks between lectures",
    "status": "verified",
    "evidence_count": 40,
    "importance": 0.8
  },
  {
    "id": "fact_lab_partners_banter",
    "category": "education",
    "badge": "College social life.",
    "confidence": "0.94",
    "content": "Alisha: Shares sarcastic commentary about lab partners and long afternoon lecture sessions",
    "status": "verified",
    "evidence_count": 35,
    "importance": 0.8
  },
  {
    "id": "fact_cozy_shows",
    "category": "preference",
    "badge": "Viewing habits.",
    "confidence": "0.95",
    "content": "Alisha: Prefers comforting, engaging romantic and mystery storylines while wrapped in warm blankets",
    "status": "verified",
    "evidence_count": 35,
    "importance": 0.8
  },
  {
    "id": "seed_alisha_study_habits",
    "category": "education",
    "badge": "Study Habits",
    "confidence": "0.96",
    "content": "Alisha: Wraps in cozy blanket while studying chemistry mechanisms with warm cup of tea",
    "status": "verified",
    "evidence_count": 22,
    "importance": 0.8
  },
  {
    "id": "fact_spilling_tea",
    "category": "habits",
    "badge": "Chai Near-Spills",
    "confidence": "1.0",
    "content": "Alisha: Clumsily almost spills chai on her study notes when rushing to reply to messages or help mum",
    "status": "verified",
    "evidence_count": 70,
    "importance": 0.75
  },
  {
    "id": "fact_study_playlists",
    "category": "education",
    "badge": "Study Music",
    "confidence": "0.95",
    "content": "Alisha: Listens to ambient soundtracks and lofi beats while working on long chemistry problem sets",
    "status": "verified",
    "evidence_count": 65,
    "importance": 0.75
  },
  {
    "id": "seed_alisha_kdramas",
    "category": "preference",
    "badge": "Kdramas",
    "confidence": "0.95",
    "content": "Alisha: Loves watching KDramas during college breaks -- gets deeply invested in storylines",
    "status": "verified",
    "evidence_count": 15,
    "importance": 0.75
  }
];

const INITIAL_VOICE_NOTES: VoiceNote[] = [
  {
    "id": 59,
    "sender": "user",
    "ts_ms": 1742312880000,
    "content": "and you've got a nice voice",
    "transcript": "and you've got a nice voice",
    "media_path": "voice/1102256372963051.wav",
    "audio_url": "/voice/1102256372963051.wav",
    "duration_sec": 66.0,
    "duration_label": "1:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 60,
    "sender": "user",
    "ts_ms": 1742312880000,
    "content": "my genitals are voice activated so...",
    "transcript": "my genitals are voice activated so...",
    "media_path": "voice/1102728112046558.wav",
    "audio_url": "/voice/1102728112046558.wav",
    "duration_sec": 11.5,
    "duration_label": "0:11",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 469,
    "sender": "user",
    "ts_ms": 1742406480000,
    "content": "I was listening to your audio message",
    "transcript": "I was listening to your audio message",
    "media_path": "voice/1106902128276641.wav",
    "audio_url": "/voice/1106902128276641.wav",
    "duration_sec": 28.3,
    "duration_label": "0:28",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 554,
    "sender": "user",
    "ts_ms": 1742465340000,
    "content": "would've been mesmerised by your majestic voice",
    "transcript": "would've been mesmerised by your majestic voice",
    "media_path": "voice/1124858656499804.wav",
    "audio_url": "/voice/1124858656499804.wav",
    "duration_sec": 18.8,
    "duration_label": "0:18",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 1288,
    "sender": "user",
    "ts_ms": 1742643180000,
    "content": "I like your voice because it's sweet and somewhat soothing",
    "transcript": "I like your voice because it's sweet and somewhat soothing",
    "media_path": "voice/1125435969717032.wav",
    "audio_url": "/voice/1125435969717032.wav",
    "duration_sec": 4.0,
    "duration_label": "0:04",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 1299,
    "sender": "user",
    "ts_ms": 1742643360000,
    "content": "your voice is actually sexy",
    "transcript": "your voice is actually sexy",
    "media_path": "voice/1152182242910495.wav",
    "audio_url": "/voice/1152182242910495.wav",
    "duration_sec": 22.5,
    "duration_label": "0:22",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2582,
    "sender": "user",
    "ts_ms": 1743518280000,
    "content": "I was listening to all the voice messages u sent me on repeat",
    "transcript": "I was listening to all the voice messages u sent me on repeat",
    "media_path": "voice/1166300782230427.wav",
    "audio_url": "/voice/1166300782230427.wav",
    "duration_sec": 13.2,
    "duration_label": "0:13",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2593,
    "sender": "user",
    "ts_ms": 1743518460000,
    "content": "I love your voice",
    "transcript": "I love your voice",
    "media_path": "voice/1168958751922864.wav",
    "audio_url": "/voice/1168958751922864.wav",
    "duration_sec": 5.0,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2684,
    "sender": "user",
    "ts_ms": 1744018380000,
    "content": "I missed your voice",
    "transcript": "I missed your voice",
    "media_path": "voice/1180869180518438.wav",
    "audio_url": "/voice/1180869180518438.wav",
    "duration_sec": 5.9,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2831,
    "sender": "user",
    "ts_ms": 1744028880000,
    "content": "I just heard u laugh in the voice message that u sent and I liked the way u laughed",
    "transcript": "I just heard u laugh in the voice message that u sent and I liked the way u laughed",
    "media_path": "voice/1191666156166874.wav",
    "audio_url": "/voice/1191666156166874.wav",
    "duration_sec": 55.0,
    "duration_label": "0:55",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.9
  },
  {
    "id": 2880,
    "sender": "user",
    "ts_ms": 1744029540000,
    "content": "your voice",
    "transcript": "your voice",
    "media_path": "voice/1200311002017121.wav",
    "audio_url": "/voice/1200311002017121.wav",
    "duration_sec": 6.4,
    "duration_label": "0:06",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2891,
    "sender": "alisha",
    "ts_ms": 1744029720000,
    "content": "no but i'm pretty sure if i was to stop sending voice messages you would forget how i sound",
    "transcript": "no but i'm pretty sure if i was to stop sending voice messages you would forget how i sound",
    "media_path": "voice/1211480357481077.wav",
    "audio_url": "/voice/1211480357481077.wav",
    "duration_sec": 53.5,
    "duration_label": "0:53",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2914,
    "sender": "alisha",
    "ts_ms": 1744030620000,
    "content": "so like whoever has sent you voice messages in the past, you still remember how they sounded",
    "transcript": "so like whoever has sent you voice messages in the past, you still remember how they sounded",
    "media_path": "voice/1242969967588294.wav",
    "audio_url": "/voice/1242969967588294.wav",
    "duration_sec": 4.0,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2917,
    "sender": "user",
    "ts_ms": 1744030680000,
    "content": "yeaaa if they had a sweet voice then yes",
    "transcript": "yeaaa if they had a sweet voice then yes",
    "media_path": "voice/1246965424286865.wav",
    "audio_url": "/voice/1246965424286865.wav",
    "duration_sec": 15.6,
    "duration_label": "0:15",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2919,
    "sender": "alisha",
    "ts_ms": 1744031040000,
    "content": "lmao just if their voice was sweet",
    "transcript": "lmao just if their voice was sweet",
    "media_path": "voice/1247080237633732.wav",
    "audio_url": "/voice/1247080237633732.wav",
    "duration_sec": 5.5,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 2997,
    "sender": "user",
    "ts_ms": 1744187940000,
    "content": "why is your voice so sweet",
    "transcript": "why is your voice so sweet",
    "media_path": "voice/1263263328564508.wav",
    "audio_url": "/voice/1263263328564508.wav",
    "duration_sec": 5.0,
    "duration_label": "0:04",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3003,
    "sender": "alisha",
    "ts_ms": 1744194900000,
    "content": "i'd miss your voice 😔",
    "transcript": "i'd miss your voice 😔",
    "media_path": "voice/1278103253999696.wav",
    "audio_url": "/voice/1278103253999696.wav",
    "duration_sec": 2.2,
    "duration_label": "0:02",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3009,
    "sender": "user",
    "ts_ms": 1744195080000,
    "content": "and u could do it to me when u want without my voice getting affected",
    "transcript": "and u could do it to me when u want without my voice getting affected",
    "media_path": "voice/1303735758283391.wav",
    "audio_url": "/voice/1303735758283391.wav",
    "duration_sec": 17.8,
    "duration_label": "0:17",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3349,
    "sender": "user",
    "ts_ms": 1745512200000,
    "content": "oh and a sweet voice too",
    "transcript": "oh and a sweet voice too",
    "media_path": "voice/1320633202341785.wav",
    "audio_url": "/voice/1320633202341785.wav",
    "duration_sec": 14.9,
    "duration_label": "0:14",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3488,
    "sender": "user",
    "ts_ms": 1745565420000,
    "content": "send cute voice messages when u can",
    "transcript": "send cute voice messages when u can",
    "media_path": "voice/1323680105919124.wav",
    "audio_url": "/voice/1323680105919124.wav",
    "duration_sec": 4.5,
    "duration_label": "0:04",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3489,
    "sender": "user",
    "ts_ms": 1745565420000,
    "content": "I miss your voice so muchhh",
    "transcript": "I miss your voice so muchhh",
    "media_path": "voice/1339295287786203.wav",
    "audio_url": "/voice/1339295287786203.wav",
    "duration_sec": 60.8,
    "duration_label": "1:00",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3614,
    "sender": "user",
    "ts_ms": 1745674080000,
    "content": "why is your voice so comforting",
    "transcript": "why is your voice so comforting",
    "media_path": "voice/1367920494789384.wav",
    "audio_url": "/voice/1367920494789384.wav",
    "duration_sec": 3.9,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3618,
    "sender": "alisha",
    "ts_ms": 1745675520000,
    "content": "i feel like my voice is a bit",
    "transcript": "i feel like my voice is a bit",
    "media_path": "voice/1374859044127888.wav",
    "audio_url": "/voice/1374859044127888.wav",
    "duration_sec": 11.9,
    "duration_label": "0:11",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3620,
    "sender": "alisha",
    "ts_ms": 1745675580000,
    "content": "so in a way it's a boring voice",
    "transcript": "so in a way it's a boring voice",
    "media_path": "voice/1386611552905331.wav",
    "audio_url": "/voice/1386611552905331.wav",
    "duration_sec": 3.2,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 3759,
    "sender": "user",
    "ts_ms": 1745757900000,
    "content": "send me a voice message in Arabic",
    "transcript": "send me a voice message in Arabic",
    "media_path": "voice/1429594825572141.wav",
    "audio_url": "/voice/1429594825572141.wav",
    "duration_sec": 6.7,
    "duration_label": "0:06",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 4347,
    "sender": "user",
    "ts_ms": 1746167520000,
    "content": "yk, stories sound better when you voice them out",
    "transcript": "yk, stories sound better when you voice them out",
    "media_path": "voice/1438278884111686.wav",
    "audio_url": "/voice/1438278884111686.wav",
    "duration_sec": 7.6,
    "duration_label": "0:07",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 4348,
    "sender": "alisha",
    "ts_ms": 1746167880000,
    "content": "suresure ill send you a voice message about it when i can",
    "transcript": "suresure ill send you a voice message about it when i can",
    "media_path": "voice/1449866003269008.wav",
    "audio_url": "/voice/1449866003269008.wav",
    "duration_sec": 5.2,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 4440,
    "sender": "user",
    "ts_ms": 1746227700000,
    "content": "you have a really nice voice",
    "transcript": "you have a really nice voice",
    "media_path": "voice/1453968255884399.wav",
    "audio_url": "/voice/1453968255884399.wav",
    "duration_sec": 7.7,
    "duration_label": "0:07",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 5026,
    "sender": "user",
    "ts_ms": 1755254220000,
    "content": "btw, I miss your voice",
    "transcript": "btw, I miss your voice",
    "media_path": "voice/1458350818592295.wav",
    "audio_url": "/voice/1458350818592295.wav",
    "duration_sec": 12.0,
    "duration_label": "0:11",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 5027,
    "sender": "alisha",
    "ts_ms": 1755254280000,
    "content": "omdssd i was thinking to just send voice messages as well because im making a lot of spelling mistakes and its taking time to erase and retype",
    "transcript": "omdssd i was thinking to just send voice messages as well because im making a lot of spelling mistakes and its taking time to erase and retype",
    "media_path": "voice/1465028061962602.wav",
    "audio_url": "/voice/1465028061962602.wav",
    "duration_sec": 4.0,
    "duration_label": "0:04",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.9
  },
  {
    "id": 5034,
    "sender": "alisha",
    "ts_ms": 1755254400000,
    "content": "what's there to miss about my voice 😭",
    "transcript": "what's there to miss about my voice 😭",
    "media_path": "voice/1499224784558091.wav",
    "audio_url": "/voice/1499224784558091.wav",
    "duration_sec": 13.0,
    "duration_label": "0:13",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 5304,
    "sender": "alisha",
    "ts_ms": 1755335280000,
    "content": "yeahg i would've asked for it since sometimes i need to play ariund with the voice messages on here to get it to work and be clear so i could send them and on ig instead but i figured it's not that deep 💪🏽",
    "transcript": "yeahg i would've asked for it since sometimes i need to play ariund with the voice messages on here to get it to work and be clear so i could send them and on ig instead but i figured it's not that deep 💪🏽",
    "media_path": "voice/1508846270240338.wav",
    "audio_url": "/voice/1508846270240338.wav",
    "duration_sec": 3.4,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 6530,
    "sender": "user",
    "ts_ms": 1755610680000,
    "content": "and I missed your voice",
    "transcript": "and I missed your voice",
    "media_path": "voice/1510407976648934.wav",
    "audio_url": "/voice/1510407976648934.wav",
    "duration_sec": 28.4,
    "duration_label": "0:28",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 6532,
    "sender": "alisha",
    "ts_ms": 1755610740000,
    "content": "my voice missed you too",
    "transcript": "my voice missed you too",
    "media_path": "voice/1511834979942376.wav",
    "audio_url": "/voice/1511834979942376.wav",
    "duration_sec": 25.6,
    "duration_label": "0:25",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 6789,
    "sender": "user",
    "ts_ms": 1756394092515,
    "content": "is it just me who likes your voice or what? damn whenever I listen to your VMs, I be kicking my feet up and smiling and shi like damn you really got a sweet voice and the accent is the cherry on top",
    "transcript": "is it just me who likes your voice or what? damn whenever I listen to your VMs, I be kicking my feet up and smiling and shi like damn you really got a sweet voice and the accent is the cherry on top",
    "media_path": "voice/1524264118925741.wav",
    "audio_url": "/voice/1524264118925741.wav",
    "duration_sec": 16.6,
    "duration_label": "0:16",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 6862,
    "sender": "alisha",
    "ts_ms": 1756399800535,
    "content": "what has that got to do with my voice messages",
    "transcript": "what has that got to do with my voice messages",
    "media_path": "voice/1532103147792788.wav",
    "audio_url": "/voice/1532103147792788.wav",
    "duration_sec": 6.5,
    "duration_label": "0:06",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7155,
    "sender": "user",
    "ts_ms": 1757394901584,
    "content": "I seriously need to make a voice assistant using your voice so I can hear this majestic voice anytime I want, it'll always be with me.",
    "transcript": "I seriously need to make a voice assistant using your voice so I can hear this majestic voice anytime I want, it'll always be with me.",
    "media_path": "voice/1534691510956187.wav",
    "audio_url": "/voice/1534691510956187.wav",
    "duration_sec": 36.9,
    "duration_label": "0:36",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7162,
    "sender": "user",
    "ts_ms": 1757401225340,
    "content": "I really really really like your voice",
    "transcript": "I really really really like your voice",
    "media_path": "voice/1535561748090412.wav",
    "audio_url": "/voice/1535561748090412.wav",
    "duration_sec": 26.3,
    "duration_label": "0:26",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7252,
    "sender": "user",
    "ts_ms": 1759071590046,
    "content": "can I make a personal assistant that has your voice and accent? like do u give me consent to use your voice?",
    "transcript": "can I make a personal assistant that has your voice and accent? like do u give me consent to use your voice?",
    "media_path": "voice/1535750000946830.wav",
    "audio_url": "/voice/1535750000946830.wav",
    "duration_sec": 17.9,
    "duration_label": "0:17",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7254,
    "sender": "alisha",
    "ts_ms": 1759072025262,
    "content": "use my voice wym",
    "transcript": "use my voice wym",
    "media_path": "voice/1576806253202733.wav",
    "audio_url": "/voice/1576806253202733.wav",
    "duration_sec": 19.0,
    "duration_label": "0:18",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7256,
    "sender": "user",
    "ts_ms": 1759072152170,
    "content": "like when u use Siri, it has a specific voice right. I wanna create a Siri of my own but it'll have your voice",
    "transcript": "like when u use Siri, it has a specific voice right. I wanna create a Siri of my own but it'll have your voice",
    "media_path": "voice/1583972892977879.wav",
    "audio_url": "/voice/1583972892977879.wav",
    "duration_sec": 21.4,
    "duration_label": "0:21",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7802,
    "sender": "user",
    "ts_ms": 1759673236281,
    "content": "as much as I enjoy your voice messages, I think I have to ask you to stop sending me them otherwise I am gonna fall in love",
    "transcript": "as much as I enjoy your voice messages, I think I have to ask you to stop sending me them otherwise I am gonna fall in love",
    "media_path": "voice/1584999422676332.wav",
    "audio_url": "/voice/1584999422676332.wav",
    "duration_sec": 3.5,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7808,
    "sender": "user",
    "ts_ms": 1759673718569,
    "content": "yk how the water droplets that keep falling on a rock penetrate through it. my heart is like that rock and your voice is like that water that keeps falling on it",
    "transcript": "yk how the water droplets that keep falling on a rock penetrate through it. my heart is like that rock and your voice is like that water that keeps falling on it",
    "media_path": "voice/1671531157593461.wav",
    "audio_url": "/voice/1671531157593461.wav",
    "duration_sec": 15.0,
    "duration_label": "0:14",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7809,
    "sender": "user",
    "ts_ms": 1759673751083,
    "content": "I think I'll inevitably end up falling in love if I keep listening to your voice messages",
    "transcript": "I think I'll inevitably end up falling in love if I keep listening to your voice messages",
    "media_path": "voice/1797741407531009.wav",
    "audio_url": "/voice/1797741407531009.wav",
    "duration_sec": 9.9,
    "duration_label": "0:09",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7810,
    "sender": "user",
    "ts_ms": 1759673800473,
    "content": "if I say that you're the woman with the best voice that I personally know then that wouldn't be wrong",
    "transcript": "if I say that you're the woman with the best voice that I personally know then that wouldn't be wrong",
    "media_path": "voice/1804651893779288.wav",
    "audio_url": "/voice/1804651893779288.wav",
    "duration_sec": 10.8,
    "duration_label": "0:10",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7811,
    "sender": "alisha",
    "ts_ms": 1759673835685,
    "content": "you'll fall in love with my voice",
    "transcript": "you'll fall in love with my voice",
    "media_path": "voice/1870167123674999.wav",
    "audio_url": "/voice/1870167123674999.wav",
    "duration_sec": 55.5,
    "duration_label": "0:55",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7812,
    "sender": "user",
    "ts_ms": 1759673838615,
    "content": "your voice gives me a serene experience, the way it bounces inside my ears and puts me in a trance",
    "transcript": "your voice gives me a serene experience, the way it bounces inside my ears and puts me in a trance",
    "media_path": "voice/1876756223268674.wav",
    "audio_url": "/voice/1876756223268674.wav",
    "duration_sec": 18.1,
    "duration_label": "0:18",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7819,
    "sender": "user",
    "ts_ms": 1759673989931,
    "content": "I mean I am gonna make my own Siri that uses your voice",
    "transcript": "I mean I am gonna make my own Siri that uses your voice",
    "media_path": "voice/1889580575292482.wav",
    "audio_url": "/voice/1889580575292482.wav",
    "duration_sec": 32.7,
    "duration_label": "0:32",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7920,
    "sender": "user",
    "ts_ms": 1759675418055,
    "content": "I get sent a voice message by this really nice woman named alisha",
    "transcript": "I get sent a voice message by this really nice woman named alisha",
    "media_path": "voice/1921002235428553.wav",
    "audio_url": "/voice/1921002235428553.wav",
    "duration_sec": 27.7,
    "duration_label": "0:27",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7925,
    "sender": "user",
    "ts_ms": 1759675505163,
    "content": "I'd love to meet u in jannah, finna listen to your voice for as long as I like and the best part it's never gonna stop getting better",
    "transcript": "I'd love to meet u in jannah, finna listen to your voice for as long as I like and the best part it's never gonna stop getting better",
    "media_path": "voice/1954195245200829.wav",
    "audio_url": "/voice/1954195245200829.wav",
    "duration_sec": 3.0,
    "duration_label": "0:02",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7944,
    "sender": "user",
    "ts_ms": 1759677631657,
    "content": "well I can't stop thinking about your voice and my infinity is the duration of my life and I've been thinking about your voice since I've heard it so ig that's infinite for me",
    "transcript": "well I can't stop thinking about your voice and my infinity is the duration of my life and I've been thinking about your voice since I've heard it so ig that's infinite for me",
    "media_path": "voice/1962096534675873.wav",
    "audio_url": "/voice/1962096534675873.wav",
    "duration_sec": 27.8,
    "duration_label": "0:27",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7954,
    "sender": "alisha",
    "ts_ms": 1759677755209,
    "content": "that's kind of you dw you gonna like your wife's voice more",
    "transcript": "that's kind of you dw you gonna like your wife's voice more",
    "media_path": "voice/1977187176416601.wav",
    "audio_url": "/voice/1977187176416601.wav",
    "duration_sec": 27.3,
    "duration_label": "0:27",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7963,
    "sender": "alisha",
    "ts_ms": 1759677840893,
    "content": "why would anyone not like the voice of their spouse",
    "transcript": "why would anyone not like the voice of their spouse",
    "media_path": "voice/2047488039345683.wav",
    "audio_url": "/voice/2047488039345683.wav",
    "duration_sec": 23.5,
    "duration_label": "0:23",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7964,
    "sender": "user",
    "ts_ms": 1759677881660,
    "content": "uhhh I mean it is very much possible to not like your spouse's voice",
    "transcript": "uhhh I mean it is very much possible to not like your spouse's voice",
    "media_path": "voice/2097467544114823.wav",
    "audio_url": "/voice/2097467544114823.wav",
    "duration_sec": 2.3,
    "duration_label": "0:02",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7968,
    "sender": "alisha",
    "ts_ms": 1759677934515,
    "content": "their voice is their voice innit",
    "transcript": "their voice is their voice innit",
    "media_path": "voice/2106340333237368.wav",
    "audio_url": "/voice/2106340333237368.wav",
    "duration_sec": 39.0,
    "duration_label": "0:39",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7969,
    "sender": "alisha",
    "ts_ms": 1759677949207,
    "content": "i like my spouse's voice",
    "transcript": "i like my spouse's voice",
    "media_path": "voice/2122853978254840.wav",
    "audio_url": "/voice/2122853978254840.wav",
    "duration_sec": 30.9,
    "duration_label": "0:30",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 7970,
    "sender": "user",
    "ts_ms": 1759677966030,
    "content": "yeah but some voices are pleasant and sweet to my ear and some aren't, it is what it is",
    "transcript": "yeah but some voices are pleasant and sweet to my ear and some aren't, it is what it is",
    "media_path": "voice/2245621169271986.wav",
    "audio_url": "/voice/2245621169271986.wav",
    "duration_sec": 15.3,
    "duration_label": "0:15",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8080,
    "sender": "user",
    "ts_ms": 1759758056144,
    "content": "idk why I keep complimenting your voice, it's not even that good",
    "transcript": "idk why I keep complimenting your voice, it's not even that good",
    "media_path": "voice/2336400673458885.wav",
    "audio_url": "/voice/2336400673458885.wav",
    "duration_sec": 23.3,
    "duration_label": "0:23",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8084,
    "sender": "user",
    "ts_ms": 1759758251954,
    "content": "my honest reaction while listening to your voice messages",
    "transcript": "my honest reaction while listening to your voice messages",
    "media_path": "voice/2380515879070579.wav",
    "audio_url": "/voice/2380515879070579.wav",
    "duration_sec": 11.4,
    "duration_label": "0:11",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8087,
    "sender": "user",
    "ts_ms": 1759761246296,
    "content": "if there was an onlyfans for voice messages, you would've been the top performer",
    "transcript": "if there was an onlyfans for voice messages, you would've been the top performer",
    "media_path": "voice/2418393615300776.wav",
    "audio_url": "/voice/2418393615300776.wav",
    "duration_sec": 30.1,
    "duration_label": "0:30",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8093,
    "sender": "alisha",
    "ts_ms": 1759761386649,
    "content": "like i don't understand what it is that yous hear from my voice that makes you think it sounds good",
    "transcript": "like i don't understand what it is that yous hear from my voice that makes you think it sounds good",
    "media_path": "voice/2442534722846746.wav",
    "audio_url": "/voice/2442534722846746.wav",
    "duration_sec": 86.7,
    "duration_label": "1:26",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8098,
    "sender": "user",
    "ts_ms": 1759761639922,
    "content": "hmm well if I had to analyse what makes me like it so much, the result would probably be that your voice is quite soothing and comforting, like a gentle wave washing over me after a long day, easing every tension with its soft, velvety warmth that makes me feel safe and seen. It's got this incredible depth, wrapping around my thoughts like a cozy embrace, drawing out a smile every time you speak, and honestly, it lingers in my mind long after, replaying that calm magic that just grounds me in the best way. but damn, when it dips low like that, it flips me into wanting to pin you down and fuck you slow until you're moaning back in that same husky tone",
    "transcript": "hmm well if I had to analyse what makes me like it so much, the result would probably be that your voice is quite soothing and comforting, like a gentle wave washing over me after a long day, easing every tension with its soft, velvety warmth that makes me feel safe and seen. It's got this incredible depth, wrapping around my thoughts like a cozy embrace, drawing out a smile every time you speak, and honestly, it lingers in my mind long after, replaying that calm magic that just grounds me in the best way. but damn, when it dips low like that, it flips me into wanting to pin you down and fuck you slow until you're moaning back in that same husky tone",
    "media_path": "voice/24767714766171544.wav",
    "audio_url": "/voice/24767714766171544.wav",
    "duration_sec": 3.8,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8100,
    "sender": "user",
    "ts_ms": 1759761712797,
    "content": "I know I'm still not doing your voice justice with my words",
    "transcript": "I know I'm still not doing your voice justice with my words",
    "media_path": "voice/2489457774858934.wav",
    "audio_url": "/voice/2489457774858934.wav",
    "duration_sec": 9.6,
    "duration_label": "0:09",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8148,
    "sender": "user",
    "ts_ms": 1759762785407,
    "content": "but I'm too busy obsessing over your voice and trying to build a bot",
    "transcript": "but I'm too busy obsessing over your voice and trying to build a bot",
    "media_path": "voice/2681640302217349.wav",
    "audio_url": "/voice/2681640302217349.wav",
    "duration_sec": 12.0,
    "duration_label": "0:11",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8328,
    "sender": "user",
    "ts_ms": 1759766731289,
    "content": "I'm probably gonna be gooning to the voice messages that you've sent but ty",
    "transcript": "I'm probably gonna be gooning to the voice messages that you've sent but ty",
    "media_path": "voice/27080375754880836.wav",
    "audio_url": "/voice/27080375754880836.wav",
    "duration_sec": 8.2,
    "duration_label": "0:08",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8568,
    "sender": "user",
    "ts_ms": 1760284538886,
    "content": "not exactly like a girlfriend, like how I enjoy listening to your voice, a certain person might enjoy listening to another person like their dad etc so we can tweak some stuff and make that work",
    "transcript": "not exactly like a girlfriend, like how I enjoy listening to your voice, a certain person might enjoy listening to another person like their dad etc so we can tweak some stuff and make that work",
    "media_path": "voice/2765063207022503.wav",
    "audio_url": "/voice/2765063207022503.wav",
    "duration_sec": 6.8,
    "duration_label": "0:06",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8570,
    "sender": "user",
    "ts_ms": 1760284583261,
    "content": "you really underestimat how good u sound. if I could, I would cream my pants to every voice message u send me",
    "transcript": "you really underestimat how good u sound. if I could, I would cream my pants to every voice message u send me",
    "media_path": "voice/3704781926495558.wav",
    "audio_url": "/voice/3704781926495558.wav",
    "duration_sec": 5.9,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8640,
    "sender": "user",
    "ts_ms": 1760287798960,
    "content": "been a fan of your voice since day q",
    "transcript": "been a fan of your voice since day q",
    "media_path": "voice/4098533317055142.wav",
    "audio_url": "/voice/4098533317055142.wav",
    "duration_sec": 2.6,
    "duration_label": "0:02",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8641,
    "sender": "user",
    "ts_ms": 1760287804543,
    "content": "been a fan of your voice since day 1 (edited)",
    "transcript": "been a fan of your voice since day 1 (edited)",
    "media_path": "voice/4220263631542830.wav",
    "audio_url": "/voice/4220263631542830.wav",
    "duration_sec": 17.2,
    "duration_label": "0:17",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8645,
    "sender": "user",
    "ts_ms": 1760288913846,
    "content": "if I'm on death row and they ask me what I wanna hear as they take me out, I'll proudly say \"Alisha's voice messages\"",
    "transcript": "if I'm on death row and they ask me what I wanna hear as they take me out, I'll proudly say \"Alisha's voice messages\"",
    "media_path": "voice/5191809857710001.wav",
    "audio_url": "/voice/5191809857710001.wav",
    "duration_sec": 7.7,
    "duration_label": "0:07",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8662,
    "sender": "user",
    "ts_ms": 1760289684902,
    "content": "okay as long as I don't get a wife or someone else whose voice I like more or someone that has great emotional importance to me or sth like that I'll go with your voice on death row",
    "transcript": "okay as long as I don't get a wife or someone else whose voice I like more or someone that has great emotional importance to me or sth like that I'll go with your voice on death row",
    "media_path": "voice/666382039189526.wav",
    "audio_url": "/voice/666382039189526.wav",
    "duration_sec": 1.8,
    "duration_label": "0:01",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 8666,
    "sender": "alisha",
    "ts_ms": 1760290260549,
    "content": "i'll even come and you can just hear me instead of voice messages",
    "transcript": "i'll even come and you can just hear me instead of voice messages",
    "media_path": "voice/675735375589288.wav",
    "audio_url": "/voice/675735375589288.wav",
    "duration_sec": 23.1,
    "duration_label": "0:23",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 9267,
    "sender": "user",
    "ts_ms": 1765070342915,
    "content": "like it's a small chunk of a big voice message",
    "transcript": "like it's a small chunk of a big voice message",
    "media_path": "voice/757065903868183.wav",
    "audio_url": "/voice/757065903868183.wav",
    "duration_sec": 26.5,
    "duration_label": "0:26",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 9482,
    "sender": "user",
    "ts_ms": 1765085064420,
    "content": "I should've just sent a voice message",
    "transcript": "I should've just sent a voice message",
    "media_path": "voice/768814752722871.wav",
    "audio_url": "/voice/768814752722871.wav",
    "duration_sec": 39.7,
    "duration_label": "0:39",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 9564,
    "sender": "alisha",
    "ts_ms": 1765094838620,
    "content": "mm no but you can get a voice message",
    "transcript": "mm no but you can get a voice message",
    "media_path": "voice/780868518105469.wav",
    "audio_url": "/voice/780868518105469.wav",
    "duration_sec": 9.6,
    "duration_label": "0:09",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 10579,
    "sender": "user",
    "ts_ms": 1765453731585,
    "content": "and I can only think of me making a personal assistant that has your voice",
    "transcript": "and I can only think of me making a personal assistant that has your voice",
    "media_path": "voice/781220244738314.wav",
    "audio_url": "/voice/781220244738314.wav",
    "duration_sec": 19.0,
    "duration_label": "0:18",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 10602,
    "sender": "user",
    "ts_ms": 1765453964119,
    "content": "imma miss your voice messages",
    "transcript": "imma miss your voice messages",
    "media_path": "voice/781366028073494.wav",
    "audio_url": "/voice/781366028073494.wav",
    "duration_sec": 5.8,
    "duration_label": "0:05",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 11007,
    "sender": "user",
    "ts_ms": 1774176451961,
    "content": "when I wasn't talking to u, I came across a few videos where people had the same accent to u and I really liked it and I started to think that maybe it's not your voice that I like but it's your accent but boy was I wrong. damn... there really is something magical about your voice.",
    "transcript": "when I wasn't talking to u, I came across a few videos where people had the same accent to u and I really liked it and I started to think that maybe it's not your voice that I like but it's your accent but boy was I wrong. damn... there really is something magical about your voice.",
    "media_path": "voice/788411510688578.wav",
    "audio_url": "/voice/788411510688578.wav",
    "duration_sec": 21.9,
    "duration_label": "0:21",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 11165,
    "sender": "user",
    "ts_ms": 1774239260296,
    "content": "I want u to send me a voice message of u reciting any surah of your choice, if you're comfortable with that. this would really mean a lot to me",
    "transcript": "I want u to send me a voice message of u reciting any surah of your choice, if you're comfortable with that. this would really mean a lot to me",
    "media_path": "voice/791724180153402.wav",
    "audio_url": "/voice/791724180153402.wav",
    "duration_sec": 8.4,
    "duration_label": "0:08",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 11193,
    "sender": "user",
    "ts_ms": 1774262478449,
    "content": "well you've got the voice of a Disney princess and if u started singing, birds would grab you by your shoulders and your arms and they would've flown u wherever u wanted",
    "transcript": "well you've got the voice of a Disney princess and if u started singing, birds would grab you by your shoulders and your arms and they would've flown u wherever u wanted",
    "media_path": "voice/792193499890998.wav",
    "audio_url": "/voice/792193499890998.wav",
    "duration_sec": 10.8,
    "duration_label": "0:10",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 11230,
    "sender": "alisha",
    "ts_ms": 1774265237997,
    "content": "i hear the voices",
    "transcript": "i hear the voices",
    "media_path": "voice/798096113348399.wav",
    "audio_url": "/voice/798096113348399.wav",
    "duration_sec": 19.6,
    "duration_label": "0:19",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 12242,
    "sender": "user",
    "ts_ms": 1774667289844,
    "content": "so I think it was eid day 2 or eid day 3 for me, around 4pm, we were talking. I was sitting on my bed and my brother came and started to look at my phone to see what I was doing. and I was texting you and the text that was visible to him was the one where I had said \"your voice is like a Disney princess\", now he looked at who I was saying that to which is you \"alisha\", he started asking \"who is this alisha\" and started laughing. there's this thing between us, I tease him by saying that this girl likes u or she was looking at you and there are some girls that I think he likes but he doesn't admit it so I just like to joke about him liking them so he always takes moments like this as an opportunity to do the same with me.",
    "transcript": "so I think it was eid day 2 or eid day 3 for me, around 4pm, we were talking. I was sitting on my bed and my brother came and started to look at my phone to see what I was doing. and I was texting you and the text that was visible to him was the one where I had said \"your voice is like a Disney princess\", now he looked at who I was saying that to which is you \"alisha\", he started asking \"who is this alisha\" and started laughing. there's this thing between us, I tease him by saying that this girl likes u or she was looking at you and there are some girls that I think he likes but he doesn't admit it so I just like to joke about him liking them so he always takes moments like this as an opportunity to do the same with me.",
    "media_path": "voice/802542409583729.wav",
    "audio_url": "/voice/802542409583729.wav",
    "duration_sec": 27.6,
    "duration_label": "0:27",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.9
  },
  {
    "id": 12243,
    "sender": "user",
    "ts_ms": 1774667791558,
    "content": "I usually don't tend to hide my phone or switch to another screen when I'm texting, I keep doing what im doing. it's a thing where I like to think that \"I'm doing wtv I want and I'm not scared of doing it infront of anybody judging me for what I'm doing\". but yeah sometimes I should really hide things to respect the other person's privacy. anyways so later that day me, my mom and my brother were sitting in my room, my mom was doing something and we all were talking about something and suddenly my brother brought u up (we usually don't talk about or joke about the girls infront of our parents but he did that). he told her how I was telling u that your voice sounds like a Disney princess. so my mom asked me your name and I told her that it's Alisha and then she asked me about where u live, I told her that you're from London and then she said \"oho, pasand ha apko? rishte ki baat kren uske ghar walon se phir?\"",
    "transcript": "I usually don't tend to hide my phone or switch to another screen when I'm texting, I keep doing what im doing. it's a thing where I like to think that \"I'm doing wtv I want and I'm not scared of doing it infront of anybody judging me for what I'm doing\". but yeah sometimes I should really hide things to respect the other person's privacy. anyways so later that day me, my mom and my brother were sitting in my room, my mom was doing something and we all were talking about something and suddenly my brother brought u up (we usually don't talk about or joke about the girls infront of our parents but he did that). he told her how I was telling u that your voice sounds like a Disney princess. so my mom asked me your name and I told her that it's Alisha and then she asked me about where u live, I told her that you're from London and then she said \"oho, pasand ha apko? rishte ki baat kren uske ghar walon se phir?\"",
    "media_path": "voice/802943512346959.wav",
    "audio_url": "/voice/802943512346959.wav",
    "duration_sec": 9.0,
    "duration_label": "0:08",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.9
  },
  {
    "id": 12724,
    "sender": "alisha",
    "ts_ms": 1774940710482,
    "content": "I had an auntie back in mauritius that started a rumour saying I was talking to a man most of the time I spent there. The thing that bugged me about that a lot was that I never called anyone apart from my wife, and her voice is deep so we've had a lot of people saying she sounds like a man. I'm like that's who the auntie heard.",
    "transcript": "I had an auntie back in mauritius that started a rumour saying I was talking to a man most of the time I spent there. The thing that bugged me about that a lot was that I never called anyone apart from my wife, and her voice is deep so we've had a lot of people saying she sounds like a man. I'm like that's who the auntie heard.",
    "media_path": "voice/807974821750413.wav",
    "audio_url": "/voice/807974821750413.wav",
    "duration_sec": 51.7,
    "duration_label": "0:51",
    "badge": "Voice Compliment",
    "category": "family",
    "importance": 0.85
  },
  {
    "id": 12844,
    "sender": "user",
    "ts_ms": 1774942325862,
    "content": "just send me a voice message of you reciting any surah of your choice before u do so",
    "transcript": "just send me a voice message of you reciting any surah of your choice before u do so",
    "media_path": "voice/811912554955330.wav",
    "audio_url": "/voice/811912554955330.wav",
    "duration_sec": 3.5,
    "duration_label": "0:03",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 13100,
    "sender": "user",
    "ts_ms": 1774948879332,
    "content": "yummy, I love men with a fat ass and a nice voice",
    "transcript": "yummy, I love men with a fat ass and a nice voice",
    "media_path": "voice/819407320874826.wav",
    "audio_url": "/voice/819407320874826.wav",
    "duration_sec": 44.1,
    "duration_label": "0:44",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  },
  {
    "id": 13590,
    "sender": "alisha",
    "ts_ms": 1775638518920,
    "content": "later i'll just send a voice message since it might be long",
    "transcript": "later i'll just send a voice message since it might be long",
    "media_path": "voice/823834583912959.wav",
    "audio_url": "/voice/823834583912959.wav",
    "duration_sec": 25.6,
    "duration_label": "0:25",
    "badge": "Voice Compliment",
    "category": "behavior",
    "importance": 0.8
  }
];

const CATEGORY_TABS = [
  { id: 'all', label: 'All (Everything)', icon: Sparkles },
  { id: 'identity', label: 'Identity & Age (20)', icon: ShieldCheck },
  { id: 'education', label: 'Biochemistry & Lab', icon: Layers },
  { id: 'personal', label: 'Faith & Daily Salah', icon: Heart },
  { id: 'preference', label: 'Cats & Kittu Stories', icon: Tag },
  { id: 'habits', label: 'Chai & Daily Routines', icon: RefreshCw },
  { id: 'kdrama', label: 'KDramas & Shows', icon: MessageSquare },
  { id: 'family', label: "Family & Mum's Kitchen", icon: Heart },
  { id: 'behavior', label: 'Voice Notes & Cadence', icon: Headphones },
  { id: 'banter', label: 'Banter & Speech Quirks', icon: Sparkles },
  { id: 'jokes', label: 'Inside Jokes & Memes', icon: Sparkles },
  { id: 'loyalty', label: 'Emotional Bond & Empathy', icon: Heart },
];

export default function MemoriesPage() {
  const [viewTab, setViewTab] = useState<'facts' | 'corpus' | 'voice'>('facts');
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Vault Facts state
  const [memories, setMemories] = useState<Memory[]>(INITIAL_FACTS);

  // Corpus messages state
  const [corpusMessages, setCorpusMessages] = useState<CorpusMessage[]>([]);
  const [corpusTotal, setCorpusTotal] = useState(13653);
  const [loadingCorpus, setLoadingCorpus] = useState(false);
  const [corpusOffset, setCorpusOffset] = useState(0);
  const [hasMoreCorpus, setHasMoreCorpus] = useState(true);

  // Voice notes state
  const [voiceNotes, setVoiceNotes] = useState<VoiceNote[]>(INITIAL_VOICE_NOTES);

  // Category counts
  const [categoryStats, setCategoryStats] = useState<Record<string, number>>({
    all: 13653,
    identity: 2568,
    education: 808,
    personal: 1137,
    preference: 1423,
    family: 1456,
    behavior: 1999,
    personality: 4262,
    banter: 2800,
    jokes: 1462,
    habits: 1120,
    kdrama: 640,
    loyalty: 890,
  });

  // Sync fresh memories from API
  useEffect(() => {
    let isMounted = true;
    async function fetchMemories() {
      try {
        const res = await fetch('/api/memories');
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.memories && data.memories.length > 0) {
            setMemories(data.memories);
          }
        }
      } catch (err) {
        console.error('Failed to load memories:', err);
      }
    }
    fetchMemories();
    return () => {
      isMounted = false;
    };
  }, []);

  // Sync fresh voice notes from API
  useEffect(() => {
    let isMounted = true;
    async function fetchVoiceNotes() {
      try {
        const res = await fetch('/api/voice/notes');
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.voice_notes && data.voice_notes.length > 0) {
            setVoiceNotes(data.voice_notes);
          }
        }
      } catch (err) {
        console.error('Failed to load voice notes:', err);
      }
    }
    fetchVoiceNotes();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch classified corpus messages when switching to corpus tab or changing filter
  useEffect(() => {
    if (viewTab !== 'corpus') return;

    let isMounted = true;
    async function fetchCorpus() {
      setLoadingCorpus(true);
      try {
        const catParam = activeFilter !== 'all' ? `&category=${activeFilter}` : '';
        const qParam = searchQuery ? `&q=${encodeURIComponent(searchQuery)}` : '';
        const res = await fetch(`/api/messages?limit=40&offset=0${catParam}${qParam}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setCorpusMessages(data.messages || []);
            setCorpusTotal(data.total || 13653);
            if (data.category_stats) {
              setCategoryStats((prev) => ({ ...prev, ...data.category_stats }));
            }
            setHasMoreCorpus(data.has_more ?? false);
            setCorpusOffset(40);
          }
        }
      } catch (err) {
        console.error('Failed to load corpus messages:', err);
      } finally {
        if (isMounted) setLoadingCorpus(false);
      }
    }
    fetchCorpus();

    return () => {
      isMounted = false;
    };
  }, [viewTab, activeFilter, searchQuery]);

  const loadMoreCorpus = async () => {
    if (loadingCorpus || !hasMoreCorpus) return;
    setLoadingCorpus(true);
    try {
      const catParam = activeFilter !== 'all' ? `&category=${activeFilter}` : '';
      const qParam = searchQuery ? `&q=${encodeURIComponent(searchQuery)}` : '';
      const res = await fetch(`/api/messages?limit=40&offset=${corpusOffset}${catParam}${qParam}`);
      if (res.ok) {
        const data = await res.json();
        setCorpusMessages((prev) => [...prev, ...(data.messages || [])]);
        setCorpusOffset((prev) => prev + 40);
        setHasMoreCorpus(data.has_more ?? false);
      }
    } catch (err) {
      console.error('Failed to load more corpus messages:', err);
    } finally {
      setLoadingCorpus(false);
    }
  };

  // Filtered vault facts
  const filteredFacts = useMemo(() => {
    return memories.filter((m) => {
      if (m.id.toLowerCase().includes('test') || m.badge.toLowerCase().includes('test')) return false;

      const categoryNorm = (m.category || '').toLowerCase();
      const badgeNorm = (m.badge || '').toLowerCase();
      const contentNorm = (m.content || '').toLowerCase();
      const filterNorm = activeFilter.toLowerCase();

      let matchesFilter = filterNorm === 'all' || categoryNorm === filterNorm;
      if (!matchesFilter) {
        if (filterNorm === 'education' && (categoryNorm === 'study' || categoryNorm === 'education' || contentNorm.includes('biochem') || contentNorm.includes('lab') || contentNorm.includes('maths'))) matchesFilter = true;
        if (filterNorm === 'identity' && (categoryNorm === 'identity' || contentNorm.includes('20 years') || contentNorm.includes('mauritius') || contentNorm.includes('heritage') || contentNorm.includes('uk'))) matchesFilter = true;
        if (filterNorm === 'personal' && (categoryNorm === 'personal' || contentNorm.includes('salah') || contentNorm.includes('fajr') || contentNorm.includes('faith') || contentNorm.includes('dua') || contentNorm.includes('sajdah'))) matchesFilter = true;
        if (filterNorm === 'preference' && (categoryNorm === 'preference' || contentNorm.includes('cat') || contentNorm.includes('kittu') || contentNorm.includes('kitten'))) matchesFilter = true;
        if (filterNorm === 'habits' && (contentNorm.includes('chai') || contentNorm.includes('tea') || contentNorm.includes('blanket') || contentNorm.includes('sleep') || contentNorm.includes('routine'))) matchesFilter = true;
        if (filterNorm === 'kdrama' && (contentNorm.includes('kdrama') || contentNorm.includes('show') || contentNorm.includes('drama') || contentNorm.includes('series'))) matchesFilter = true;
        if (filterNorm === 'family' && (categoryNorm === 'family' || contentNorm.includes('mum') || contentNorm.includes('kitchen') || contentNorm.includes('daughter'))) matchesFilter = true;
        if (filterNorm === 'behavior' && (categoryNorm === 'behavior' || contentNorm.includes('voice') || contentNorm.includes('burst') || contentNorm.includes('lowercase'))) matchesFilter = true;
        if (filterNorm === 'banter' && (categoryNorm === 'personality' || contentNorm.includes('omg') || contentNorm.includes('slang') || contentNorm.includes('sarcasm'))) matchesFilter = true;
        if (filterNorm === 'jokes' && (contentNorm.includes('pattern up') || contentNorm.includes('latw') || contentNorm.includes('bubbzieee') || contentNorm.includes('omdssd') || contentNorm.includes('joke'))) matchesFilter = true;
        if (filterNorm === 'loyalty' && (contentNorm.includes('loyalty') || contentNorm.includes('empath') || contentNorm.includes('care') || contentNorm.includes('listening'))) matchesFilter = true;
      }

      const searchNorm = searchQuery.toLowerCase();
      const matchesSearch =
        !searchQuery ||
        contentNorm.includes(searchNorm) ||
        badgeNorm.includes(searchNorm) ||
        categoryNorm.includes(searchNorm);

      return matchesFilter && matchesSearch;
    });
  }, [memories, activeFilter, searchQuery]);

  // Filtered voice notes
  const filteredVoiceNotes = useMemo(() => {
    return voiceNotes.filter((vn) => {
      const contentNorm = (vn.content || '').toLowerCase();
      const badgeNorm = (vn.badge || '').toLowerCase();
      const searchNorm = searchQuery.toLowerCase();

      const matchesSearch =
        !searchQuery ||
        contentNorm.includes(searchNorm) ||
        badgeNorm.includes(searchNorm) ||
        vn.id.toString().includes(searchNorm);

      if (activeFilter === 'all') return matchesSearch;
      if (activeFilter === 'behavior') return matchesSearch;
      if (activeFilter === 'preference' && (contentNorm.includes('cat') || contentNorm.includes('kittu') || contentNorm.includes('cute'))) return matchesSearch;
      if (activeFilter === 'education' && (contentNorm.includes('exam') || contentNorm.includes('study') || contentNorm.includes('uni'))) return matchesSearch;
      if (activeFilter === 'habits' && (contentNorm.includes('tea') || contentNorm.includes('chai') || contentNorm.includes('tired') || contentNorm.includes('sleep'))) return matchesSearch;
      if (activeFilter === 'banter' && (contentNorm.includes('lol') || contentNorm.includes('voice') || contentNorm.includes('haha'))) return matchesSearch;

      return matchesSearch;
    });
  }, [voiceNotes, activeFilter, searchQuery]);

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 lg:px-10 py-6 flex flex-col gap-5 scrollbar-none pb-28 text-ivory select-none max-w-5xl mx-auto w-full">
      {/* Top Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-amber uppercase font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-amber animate-pulse" />
            DEEP CORPUS MEMORY VAULT
          </span>
          <h1 className="font-serif text-2xl sm:text-3xl font-normal text-ivory">Shared Memories</h1>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-amber uppercase tracking-widest bg-amber/10 border border-amber/20 px-3 py-1.5 rounded-full font-mono flex items-center gap-1.5 shadow-[0_0_10px_rgba(212,168,83,0.15)]">
            <ShieldCheck className="w-3 h-3 text-amber" />
            <span>{memories.length} Facts &bull; 87 Voice &bull; 13.6k Msgs</span>
          </span>
        </div>
      </div>

      {/* 3-Tab Segmented Mode Switcher */}
      <div className="grid grid-cols-3 p-1 rounded-2xl bg-surface border border-hairline shrink-0 shadow-lg">
        <button
          onClick={() => setViewTab('facts')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'facts'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Vault ({memories.length})</span>
        </button>

        <button
          onClick={() => setViewTab('voice')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'voice'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <Mic className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Voice Notes ({voiceNotes.length})</span>
        </button>

        <button
          onClick={() => setViewTab('corpus')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'corpus'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">All Msgs (13.6k)</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative shrink-0">
        <Search className="w-4 h-4 text-muted absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={
            viewTab === 'facts'
              ? 'Search 68+ verified facts (biochem, cats, faith, age 20, Mauritius...)'
              : viewTab === 'voice'
              ? 'Search 87 Instagram voice notes & audio transcripts...'
              : 'Search 13,653 classified chat & audio messages...'
          }
          className="w-full bg-surface border border-hairline focus:border-amber/50 rounded-2xl pl-10 pr-4 py-2.5 text-[13.5px] text-ivory placeholder:text-muted/60 outline-none transition-all focus:shadow-[0_0_14px_rgba(212,168,83,0.18)]"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-3.5 top-2.5 text-xs text-muted hover:text-ivory cursor-pointer"
          >
            Clear
          </button>
        )}
      </div>

      {/* Expanded Filter Category Pills */}
      <div className="flex gap-2 overflow-x-auto py-1.5 scrollbar-none shrink-0 min-h-[46px] items-center">
        {CATEGORY_TABS.map((f) => {
          const isSelected = activeFilter === f.id;
          const count =
            viewTab === 'facts'
              ? f.id === 'all'
                ? memories.length
                : memories.filter((m) => {
                    const c = (m.category || '').toLowerCase();
                    const txt = (m.content || '').toLowerCase();
                    if (f.id === 'identity') return c === 'identity' || txt.includes('age') || txt.includes('mauritius');
                    if (f.id === 'education') return c === 'education' || txt.includes('biochem') || txt.includes('maths');
                    if (f.id === 'personal') return c === 'personal' || txt.includes('salah') || txt.includes('faith');
                    if (f.id === 'preference') return c === 'preference' || txt.includes('cat') || txt.includes('kittu');
                    if (f.id === 'habits') return txt.includes('chai') || txt.includes('tea') || txt.includes('routine');
                    if (f.id === 'kdrama') return txt.includes('drama') || txt.includes('show');
                    if (f.id === 'family') return c === 'family' || txt.includes('mum');
                    if (f.id === 'behavior') return c === 'behavior' || txt.includes('voice');
                    if (f.id === 'banter') return c === 'personality' || txt.includes('omg');
                    if (f.id === 'jokes') return txt.includes('pattern') || txt.includes('latw') || txt.includes('bubbzieee');
                    if (f.id === 'loyalty') return txt.includes('loyalty') || txt.includes('empath');
                    return c === f.id;
                  }).length
              : viewTab === 'voice'
              ? f.id === 'all'
                ? voiceNotes.length
                : voiceNotes.filter((v) => {
                    const txt = (v.content || '').toLowerCase();
                    if (f.id === 'preference') return txt.includes('cat') || txt.includes('kittu');
                    if (f.id === 'education') return txt.includes('exam') || txt.includes('study');
                    if (f.id === 'habits') return txt.includes('tea') || txt.includes('tired');
                    return true;
                  }).length
              : categoryStats[f.id] || (f.id === 'all' ? 13653 : 1200);

          return (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              className={`px-3.5 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all border shrink-0 cursor-pointer shadow-sm flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-amber text-black border-amber shadow-[0_0_12px_rgba(212,168,83,0.3)] font-bold scale-[1.02]'
                  : 'bg-white/[0.04] border-white/10 text-muted hover:text-ivory hover:bg-white/[0.08]'
              }`}
            >
              <span>{f.label}</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                  isSelected ? 'bg-black/25 text-black font-bold' : 'bg-white/[0.08] text-muted'
                }`}
              >
                {count.toLocaleString()}
              </span>
            </button>
          );
        })}
      </div>

      {/* ── TAB 1: VERIFIED VAULT FACTS ── */}
      {viewTab === 'facts' && (
        <div>
          {filteredFacts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {filteredFacts.map((m) => (
                <MemoryCard
                  key={m.id}
                  badge={m.badge}
                  confidence={m.confidence}
                  content={m.content}
                  status={m.status}
                  evidence_count={m.evidence_count}
                  category={m.category}
                />
              ))}
            </div>
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No memories found in this category filter.</p>
              <p className="text-muted text-xs">Try selecting 'All (Everything)' or clear your search terms.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer hover:bg-amber/30 transition-all"
              >
                Reset to All ({memories.length} Facts)
              </button>
            </div>
          )}

          <p className="text-center text-[11px] text-muted/60 mt-3 font-mono">
            Showing {filteredFacts.length} of {memories.length} verified facts from Alisha's corpus
          </p>
        </div>
      )}

      {/* ── TAB 2: INSTAGRAM VOICE NOTES (87 AUDIO MESSAGES WITH EXACT DURATIONS) ── */}
      {viewTab === 'voice' && (
        <div className="flex flex-col gap-3.5">
          <div className="bg-gradient-to-br from-[#1C1D1A] to-[#141512] border border-amber/25 rounded-3xl p-4 shadow-lg flex items-center justify-between gap-3">
            <div>
              <div className="text-[11px] font-mono text-amber uppercase font-semibold flex items-center gap-1">
                <Headphones className="w-3.5 h-3.5 text-amber" />
                INSTAGRAM VOICE ARCHIVE
              </div>
              <h3 className="text-sm font-semibold text-ivory mt-0.5">
                87 Authentic Voice Notes from Alisha
              </h3>
              <p className="text-xs text-muted mt-0.5">
                Real audio notes with exact WAV durations, transcripts & responsive waveforms.
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-amber/15 border border-amber/30 flex items-center justify-center text-amber shrink-0">
              <Volume2 className="w-5 h-5" />
            </div>
          </div>

          {filteredVoiceNotes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {filteredVoiceNotes.map((vn, idx) => (
                <div
                  key={vn.id || idx}
                  className="p-4 rounded-3xl bg-surface/90 border border-hairline hover:border-amber/35 transition-all space-y-3 shadow-md group"
                >
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber shadow-[0_0_8px_#D4A853]" />
                      <span className="font-semibold text-ivory text-sm">Alisha</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber/10 border border-amber/20 text-amber font-medium">
                        {vn.badge || 'Instagram Voice Note'}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-muted/70">
                      Clip #{vn.id} &bull; {vn.duration_label || '0:12'}
                    </span>
                  </div>

                  {/* Audio Waveform Player with Real Duration */}
                  <div className="w-full">
                    <VoiceBubble
                      audioSrc={vn.audio_url || `/voice/${vn.media_path}`}
                      durationLabel={vn.duration_label || '0:12'}
                      duration={vn.duration_sec || 12}
                    />
                  </div>

                  {/* Authentic Transcript Box */}
                  <div className="bg-[#121310] border border-white/[0.04] rounded-2xl p-3 text-xs text-ivory/90 leading-relaxed font-sans flex items-start gap-2.5">
                    <Mic className="w-3.5 h-3.5 text-amber shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <span className="text-[10px] uppercase font-mono text-muted block mb-0.5">Voice related messages</span>
                      <span className="italic">"{vn.transcript || vn.content}"</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No voice notes matched this filter.</p>
              <p className="text-muted text-xs">Try selecting 'All' or clearing your search.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer hover:bg-amber/30 transition-all"
              >
                Reset Voice Notes
              </button>
            </div>
          )}

          <p className="text-center text-[11px] text-muted/60 mt-3 font-mono">
            Showing {filteredVoiceNotes.length} of {voiceNotes.length} Instagram voice messages
          </p>
        </div>
      )}

      {/* ── TAB 3: 13,653 CLASSIFIED CORPUS INTERACTIONS ── */}
      {viewTab === 'corpus' && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between text-xs text-muted font-mono px-1">
            <span>Classified Corpus Messages ({corpusTotal.toLocaleString()})</span>
            <span className="capitalize text-amber font-semibold">{activeFilter} filter</span>
          </div>

          {loadingCorpus && corpusMessages.length === 0 ? (
            <div className="flex flex-col gap-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-20 bg-surface border border-hairline rounded-3xl animate-pulse" />
              ))}
            </div>
          ) : corpusMessages.length > 0 ? (
            <>
              {corpusMessages.map((msg) => {
                const isAlisha = msg.sender === 'alisha';
                return (
                  <div
                    key={msg.id}
                    className="p-3.5 rounded-3xl bg-surface/80 border border-hairline hover:border-amber/25 transition-all space-y-2 shadow-sm"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            isAlisha ? 'bg-amber shadow-[0_0_6px_#D4A853]' : 'bg-blue-400'
                          }`}
                        />
                        <span className="font-semibold text-ivory">
                          {isAlisha ? 'Alisha' : 'You'}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/10 text-muted">
                          {msg.badge}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-muted/60">
                        #{msg.id}
                      </span>
                    </div>

                    {msg.is_voice ? (
                      <div className="pt-1">
                        <VoiceBubble
                          audioSrc={msg.media_path.startsWith('/') ? msg.media_path : `/${msg.media_path}`}
                          durationLabel={msg.duration_label || '0:12'}
                          duration={msg.duration_sec || 12}
                        />
                      </div>
                    ) : (
                      <p className="text-[13.5px] text-ivory/95 font-sans leading-relaxed break-words">
                        {msg.content}
                      </p>
                    )}
                  </div>
                );
              })}

              {hasMoreCorpus && (
                <button
                  onClick={loadMoreCorpus}
                  disabled={loadingCorpus}
                  className="w-full py-3 rounded-2xl bg-surface hover:bg-white/[0.08] border border-hairline text-xs font-semibold text-ivory flex items-center justify-center gap-2 transition-all active:scale-98 cursor-pointer mt-2"
                >
                  {loadingCorpus ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber" />
                  ) : (
                    <Layers className="w-3.5 h-3.5 text-amber" />
                  )}
                  <span>{loadingCorpus ? 'Loading Messages...' : 'Load More Messages (Next 40)'}</span>
                </button>
              )}
            </>
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No corpus messages matched this filter.</p>
              <p className="text-muted text-xs">Try selecting 'All (Everything)' or clear search.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer"
              >
                Reset to All
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
