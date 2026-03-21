# Implementation Plan: AI Character Chat System

## Overview

This implementation plan breaks down the AI Character Chat System into discrete coding tasks. The system is a memory-based agent that forms long-term relationships with users through LangGraph-based multi-agent orchestration, Memory Stream architecture, and advanced retrieval mechanisms.

The implementation follows a bottom-up approach: starting with foundational infrastructure (database, LLM abstraction), then building core memory systems, followed by agent components, and finally integrating everything into the main workflow with WebSocket communication.

## Tasks

- [-] 1. Set up project infrastructure and directory structure
  - ~~Create the full directory skeleton under `src/`~~ ✅ Done
  - ~~Migrate existing files to `src/core/config.py`, `src/database/connection.py`, `src/database/models.py`~~ ✅ Done
  - ~~Update `pyproject.toml` with all required dependencies~~ ✅ Done
  - ~~Create `tests/` directory structure~~ ✅ Done
  - [-] 1.1 Set up Alembic migration system
    - Run `alembic init src/database/migrations/`
    - Configure `env.py` to use async engine and import all SQLAlchemy models from `src/database/models.py`
    - Create initial migration for all tables (person, message, observation, episode, reflection, user_portrait, emotion_record, interest, dialogue_plan, memory_access_history, tag tables) with HNSW vector indexes
    - _Requirements: 11.5, 11.6_
  - [ ] 1.2 Create utility scripts and config files
    - Create `scripts/setup_db.py` to initialize pgvector extension and run migrations
    - Create `scripts/seed_data.py` for initial character data
    - Create `config/development.yaml`, `config/production.yaml`, `config/test.yaml`
    - Create `tests/conftest.py` with shared fixtures (async DB session, test client)
    - _Requirements: 11.5, 11.8_
  - [ ]* 1.3 Write unit tests for database connection and schema validation
    - Test database connection pooling
    - Test schema creation and migrations
    - Test vector index creation
    - _Requirements: 11.5, 11.6_

- [ ] 2. Implement LLM Abstraction Layer
  - [ ] 2.1 Create LLMProvider protocol interface with generate() and stream() methods
    - Define Protocol with generate, stream, get_token_count methods
    - Create standard request/response data structures
    - _Requirements: 1.1, 1.6, 1.7, 11.4_
  
  - [ ] 2.2 Implement LLMAdapter with plugin registration system
    - Create provider registry (Dict[str, LLMProvider])
    - Implement register_provider() and set_default_provider()
    - Implement generate() and stream() with provider selection
    - Add error handling and standard error responses
    - _Requirements: 1.1, 1.4, 1.5, 1.8, 1.9_
  
  - [ ] 2.3 Implement cloud LLM providers (OpenAI, Anthropic, Google)
    - Create OpenAIProvider implementing LLMProvider protocol
    - Create AnthropicProvider implementing LLMProvider protocol
    - Create GoogleProvider implementing LLMProvider protocol
    - Handle API authentication and rate limiting
    - _Requirements: 1.2, 1.6, 1.7_
  
  - [ ] 2.4 Implement local LLM providers (Ollama, LM Studio, LocalAI)
    - Create OllamaProvider implementing LLMProvider protocol
    - Create LMStudioProvider implementing LLMProvider protocol
    - Create LocalAIProvider implementing LLMProvider protocol
    - _Requirements: 1.3, 1.6, 1.7_
  
  - [ ]* 2.5 Write unit tests for LLM Adapter
    - Test provider registration and switching
    - Test request/response format conversion
    - Test error handling and fallback behavior
    - _Requirements: 1.1, 1.4, 1.5, 1.8, 1.9_

- [ ] 3. Checkpoint - Ensure database and LLM abstraction tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement Memory Stream core components
  - [ ] 4.1 Create Memory data models and base classes
    - Define Memory dataclass with id, user_id, content, memory_type, importance_score, created_at, last_access_time, embedding, metadata
    - Define MemoryType enum (MESSAGE, OBSERVATION, EPISODE, REFLECTION)
    - Create Message, Observation, Episode, Reflection dataclasses
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 4.2 Implement embedding service for vector generation
    - Create EmbeddingService with embed() method
    - Integrate with LLM providers for embedding generation
    - Add caching for embeddings
    - _Requirements: 3.7, 11.4_
  
  - [ ] 4.3 Implement MemoryStream class for message and observation management
    - Implement add_message() to store messages in database
    - Implement create_observation() to convert messages to observations
    - Implement get_recent_memories() to fetch recent memories
    - Implement update_access_time() to track memory access
    - Generate embeddings for all memory objects
    - _Requirements: 3.1, 3.2, 3.3, 3.8, 3.11_
  
  - [ ]* 4.4 Write unit tests for Memory Stream
    - Test message storage and retrieval
    - Test observation creation from messages
    - Test access time updates
    - Test embedding generation
    - _Requirements: 3.1, 3.2, 3.3, 3.8_

- [ ] 5. Implement Memory Evolution Engine
  - [ ] 5.1 Create Memory Evolution Engine with forgetting curve logic
    - Implement calculate_memory_strength() with time decay formula
    - Implement apply_forgetting_curve() with exponential decay
    - Implement reinforce_memory() to increase strength on access
    - Implement decay_unused_memories() to identify weak memories
    - Implement get_memory_access_history() to track access patterns
    - _Requirements: 3.7.4, 3.7.5, 3.7.6, 3.7.9, 3.7.11, 3.7.12_
  
  - [ ] 5.2 Implement memory access tracking and history recording
    - Create record_access() to log memory access in memory_access_history table
    - Track access context and reinforcement application
    - Update access_count on memory objects
    - _Requirements: 3.7.7, 3.8_
  
  - [ ]* 5.3 Write unit tests for Memory Evolution Engine
    - Test memory strength calculation with time decay
    - Test forgetting curve application
    - Test memory reinforcement on access
    - Test access history tracking
    - _Requirements: 3.7.4, 3.7.5, 3.7.6, 3.7.9_

- [ ] 6. Implement advanced Retrieval Engine
  - [ ] 6.1 Create RetrievalEngine with multi-factor scoring
    - Implement calculate_retrieval_score() combining Recency + Memory_Strength + Relevance
    - Implement retrieve() with vector search and score calculation
    - Integrate with Memory Evolution Engine for strength calculation
    - Implement Top-K selection based on retrieval scores
    - Update last_access_time for retrieved memories
    - _Requirements: 3.5, 3.6, 3.7, 3.8, 3.7.11_
  
  - [ ] 6.2 Implement RetrievalConfig and weight management
    - Create RetrievalConfig dataclass with top_k, weights, memory_types, time_range
    - Create RetrievalWeights dataclass with recency, importance, relevance weights
    - Allow configurable weight tuning
    - _Requirements: 3.6, 3.12_
  
  - [ ]* 6.3 Write unit tests for Retrieval Engine
    - Test retrieval score calculation
    - Test vector search integration
    - Test Top-K selection
    - Test weight configuration
    - _Requirements: 3.5, 3.6, 3.7, 3.12_

- [ ] 7. Checkpoint - Ensure memory system tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Reflection system
  - [ ] 8.1 Create ReflectionGenerator for higher-level inference
    - Implement should_generate_reflection() to check importance threshold
    - Implement generate_reflection() using LLM to infer patterns from observations
    - Implement store_reflection() to save reflections with source tracking
    - Track reflection sources in reflection_source table
    - Calculate importance_score for reflections
    - _Requirements: 3.5.1, 3.5.2, 3.5.3, 3.5.4, 3.5.5, 3.5.6, 3.5.7_
  
  - [ ]* 8.2 Write unit tests for Reflection Generator
    - Test reflection generation trigger conditions
    - Test reflection content quality
    - Test source tracking
    - _Requirements: 3.5.1, 3.5.2, 3.5.3, 3.5.7_

- [ ] 9. Implement Episode management
  - [ ] 9.1 Create EpisodeManager for meaningful event grouping
    - Implement create_episode() with purpose, turning_point, conclusion, emotion_changes
    - Implement get_episode() to retrieve episode data
    - Implement update_episode_status() to mark episodes as ONGOING or COMPLETED
    - Store episode-message relationship via `message.episode_id` FK
    - Generate embeddings for episodes
    - _Requirements: 3.4, 3.9, 3.10, 3.12_
  
  - [ ]* 9.2 Write unit tests for Episode Manager
    - Test episode creation with metadata
    - Test episode status updates
    - Test message-episode associations
    - _Requirements: 3.9, 3.10_

- [ ] 10. Implement User Portrait system
  - [ ] 10.1 Create UserPortraitManager for user profile generation
    - Implement build_portrait_from_reflections() to synthesize user profile from reflections
    - Implement update_portrait() to incrementally update profile with new reflections
    - Implement get_portrait() to retrieve current user profile
    - Implement get_portrait_confidence() to calculate confidence score
    - Store portraits in user_portrait table with personality_traits, communication_style, interests, preferences
    - _Requirements: 3.7.1, 3.7.2, 3.7.3, 3.7.8, 3.7.10, 3.7.13_
  
  - [ ]* 10.2 Write unit tests for User Portrait Manager
    - Test portrait generation from reflections
    - Test portrait updates with new reflections
    - Test confidence score calculation
    - _Requirements: 3.7.1, 3.7.2, 3.7.3, 3.7.10_

- [ ] 11. Checkpoint - Ensure reflection, episode, and portrait tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement Emotion Agent
  - [ ] 12.1 Create EmotionAgent for emotion analysis and management
    - Implement analyze_user_emotion() to extract emotion dimensions from messages
    - Implement update_character_emotion() to update AI emotion state
    - Implement get_emotion_history() to retrieve emotion records
    - Store emotion records in emotion_record table with joy, sadness, anger, surprise, fear, disgust dimensions
    - _Requirements: 5.1, 5.2, 5.3, 5.5_
  
  - [ ] 12.2 Create EmotionOrchestrator as LangGraph subgraph
    - Create StateGraph with nodes: analyze_user_emotion, update_ai_emotion, save_history, check_extreme_emotion, handle_extreme_emotion
    - Add conditional edges for extreme emotion handling
    - Define EmotionState dataclass with user_emotion, ai_emotion, trigger_reason, is_extreme
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6_
  
  - [ ]* 12.3 Write unit tests for Emotion Agent
    - Test emotion analysis accuracy
    - Test emotion state updates
    - Test emotion history tracking
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [ ] 13. Implement Planning Agent
  - [ ] 13.1 Create PlanningAgent for dialogue goal setting
    - Implement set_dialogue_goal() to define current conversation objective
    - Implement plan_response_strategy() to determine response intention
    - Implement update_plan() to adjust plan based on new context
    - Store dialogue plans in dialogue_plan table
    - Define DialogueGoal and ResponseStrategy dataclasses
    - _Requirements: 4.5.1, 4.5.2, 4.5.4, 4.5.7, 4.5.9_
  
  - [ ]* 13.2 Write unit tests for Planning Agent
    - Test dialogue goal setting
    - Test response strategy planning
    - Test plan updates
    - _Requirements: 4.5.1, 4.5.2, 4.5.4_

- [ ] 14. Implement Conversation Policy
  - [ ] 14.1 Create ConversationPolicy for natural dialogue rules
    - Implement should_ask_question() to limit consecutive questions
    - Implement should_initiate_conversation() to determine proactive engagement
    - Implement should_change_topic() to detect topic transition needs
    - Implement get_response_style() to mix short reactions and long explanations
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.10_
  
  - [ ]* 14.2 Write unit tests for Conversation Policy
    - Test consecutive question limiting
    - Test conversation initiation logic
    - Test topic change detection
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 15. Implement Topic Recommender
  - [ ] 15.1 Create TopicRecommender for interest analysis
    - Implement extract_interests() to identify user interests from conversations
    - Implement recommend_topics() to suggest relevant topics
    - Implement update_interest_profile() to learn from user reactions
    - Store interests in interest table with confidence, frequency tracking
    - _Requirements: 6.1, 6.3, 6.4, 6.5_
  
  - [ ]* 15.2 Write unit tests for Topic Recommender
    - Test interest extraction
    - Test topic recommendation
    - Test interest profile updates
    - _Requirements: 6.1, 6.3, 6.5_

- [ ] 16. Checkpoint - Ensure agent component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement LangGraph Chain Components
  - [ ] 17.1 Create AutonomousBehaviorChain for action decision
    - Implement ainvoke() to decide between respond, silence, initiate actions
    - Analyze conversation flow, emotion state, time intervals
    - Return BehaviorDecision with should_respond, action_type, reason
    - _Requirements: 9.1, 9.2, 9.3, 9.7_
  
  - [ ] 17.2 Create MemoryRetrievalChain for context gathering
    - Implement ainvoke() to retrieve relevant memories
    - Integrate with RetrievalEngine and Memory Evolution Engine
    - Update access times and reinforce accessed memories
    - _Requirements: 3.5, 3.6, 3.7, 3.8_
  
  - [ ] 17.3 Create DialoguePlanningChain for goal setting
    - Implement ainvoke() to set dialogue goals and response intentions
    - Integrate with PlanningAgent
    - Return DialoguePlan with current_goal, response_intention, expected_outcome
    - _Requirements: 4.5.1, 4.5.2, 4.5.4, 4.5.5_
  
  - [ ] 17.4 Create ConversationPolicyChain for policy validation
    - Implement ainvoke() to check conversation policy rules
    - Return PolicyCheckResult with violations and suggestions
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 17.5 Create MessageGenerationChain for response creation
    - Implement ainvoke() for single response generation
    - Implement astream() for streaming response generation
    - Build prompt with context, memories, dialogue plan, user portrait, character persona
    - Integrate with LLMAdapter
    - _Requirements: 2.2, 2.3, 3.7.8, 4.6, 4.8_
  
  - [ ]* 17.6 Write unit tests for chain components
    - Test each chain's ainvoke() method
    - Test state passing between chains
    - Test error handling
    - _Requirements: 3.5, 4.5.1, 9.1_

- [ ] 18. Implement Memory Save Orchestrator
  - [ ] 18.1 Create MemorySaveOrchestrator as LangGraph subgraph
    - Create StateGraph with nodes: save_message, create_observation, calculate_importance, check_reflection_trigger, generate_reflection, update_user_portrait
    - Add conditional edges for reflection generation
    - Define MemorySaveState dataclass
    - Integrate with MemoryStream, ReflectionGenerator, UserPortraitManager
    - _Requirements: 3.1, 3.2, 3.3, 3.5.3, 3.7.3_
  
  - [ ]* 18.2 Write integration tests for Memory Save Orchestrator
    - Test full memory save flow
    - Test reflection trigger conditions
    - Test portrait update integration
    - _Requirements: 3.1, 3.5.3, 3.7.3_

- [ ] 19. Implement Main Workflow with LangGraph
  - [ ] 19.1 Create MainConversationChain as LangGraph StateGraph
    - Define ConversationState dataclass with all required fields
    - Create StateGraph with nodes: autonomous_behavior, memory_retrieval, emotion_analysis, dialogue_planning, policy_check, message_generation, memory_save
    - Add edges connecting all nodes in sequence
    - Add conditional edges for autonomous_behavior (respond vs silence)
    - Compile graph into executable workflow
    - _Requirements: 4.5.1, 9.1, 9.2, 11.3_
  
  - [ ] 19.2 Implement ainvoke() and astream() for main workflow
    - Implement ainvoke() to execute full conversation flow
    - Implement astream() for streaming responses
    - Handle early termination (silence decision)
    - Add error handling and retry logic
    - _Requirements: 7.3, 7.4, 11.2_
  
  - [ ]* 19.3 Write integration tests for main workflow
    - Test full conversation flow from message to response
    - Test conditional branching (respond vs silence)
    - Test error handling and recovery
    - _Requirements: 9.1, 9.2, 11.3_

- [ ] 20. Checkpoint - Ensure workflow integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Implement Character Persona management
  - [ ] 21.1 Create CharacterPersona data model and storage
    - Define CharacterPersona dataclass with name, personality, speaking_style, background, behavior_patterns, system_prompt
    - Create database table or configuration file for persona storage
    - Implement load_persona() and save_persona() methods
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 21.2 Write unit tests for Character Persona
    - Test persona loading and saving
    - Test persona consistency in responses
    - _Requirements: 2.2, 2.3, 2.4_

- [ ] 22. Implement WebSocket Server
  - [ ] 22.1 Create FastAPI WebSocket server with connection management
    - Implement connect() to establish WebSocket connections
    - Implement disconnect() to clean up connections
    - Implement receive_message() to handle incoming messages
    - Implement send_message() to send responses
    - Implement stream_response() for streaming AI responses
    - Manage concurrent user sessions
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6, 11.2_
  
  - [ ] 22.2 Implement WebSocket reconnection and state restoration
    - Add reconnection logic with exponential backoff
    - Implement conversation state restoration on reconnect
    - Use message queue to prevent message loss
    - _Requirements: 7.5_
  
  - [ ]* 22.3 Write integration tests for WebSocket server
    - Test connection establishment and termination
    - Test message sending and receiving
    - Test streaming responses
    - Test reconnection and state restoration
    - Test concurrent user sessions
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 23. Implement security and privacy features
  - [ ] 23.1 Add data encryption and user isolation
    - Implement database-level encryption for conversation data
    - Add TLS/SSL configuration for WebSocket connections
    - Implement user authentication and authorization
    - Add user data isolation in database queries
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 23.2 Implement PII masking and data retention policies
    - Create PII detection and masking before LLM transmission
    - Implement data retention policy with automatic deletion
    - _Requirements: 10.5, 10.6_
  
  - [ ]* 23.3 Write security tests
    - Test data encryption
    - Test user isolation
    - Test PII masking
    - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [ ] 24. Implement context window management
  - [ ] 24.1 Create token counting and context pruning
    - Implement get_token_count() for all LLM providers
    - Create context pruning logic to stay under 200,000 token limit
    - Prioritize recent messages and high-importance memories
    - Remove low-strength memories when context overflows
    - _Requirements: 11.7, 11.9, 11.10_
  
  - [ ]* 24.2 Write tests for context window management
    - Test token counting accuracy
    - Test context pruning logic
    - Test minimum context preservation
    - _Requirements: 11.7, 11.9, 11.10_

- [ ] 25. Implement background jobs for memory evolution
  - [ ] 25.1 Create scheduled job for daily memory evolution
    - Implement apply_daily_memory_evolution() to decay unused memories
    - Update user portraits based on recent reflections
    - Archive weak memories below strength threshold
    - Schedule job to run daily (e.g., midnight)
    - _Requirements: 3.7.4, 3.7.6, 3.7.9_
  
  - [ ]* 25.2 Write tests for background jobs
    - Test memory decay application
    - Test portrait updates
    - Test memory archival
    - _Requirements: 3.7.4, 3.7.6_

- [ ] 26. Implement tag-based keyword indexing
  - [ ] 26.1 Create tag extraction and indexing system
    - Implement extract_keywords() to identify tags from messages
    - Store tags in tag table with associations to messages, observations, reflections, episodes
    - Implement tag-based search as fallback for vector search failures
    - _Requirements: 3.11_
  
  - [ ]* 26.2 Write tests for tag system
    - Test keyword extraction
    - Test tag associations
    - Test tag-based search
    - _Requirements: 3.11_

- [ ] 27. Wire all components together and create main application entry point
  - [ ] 27.1 Create main FastAPI application with dependency injection
    - Initialize all components (LLMAdapter, MemoryStream, agents, chains)
    - Register LLM providers (OpenAI, Anthropic, Google, Ollama, etc.)
    - Set up database connection pool
    - Configure WebSocket routes
    - Add health check and status endpoints
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 11.2, 11.8_
  
  - [ ] 27.2 Create configuration management and environment setup
    - Load configuration from environment variables
    - Set up logging and monitoring
    - Configure error handling middleware
    - Add API versioning support
    - _Requirements: 8.6, 11.8_
  
  - [ ]* 27.3 Write end-to-end integration tests
    - Test complete user conversation flow
    - Test memory persistence and retrieval across sessions
    - Test reflection generation and portrait updates
    - Test autonomous behavior and proactive engagement
    - _Requirements: 4.5.3, 4.5.8, 9.4, 9.6_

- [ ] 28. Final checkpoint - Run all tests and verify system functionality
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation follows a bottom-up approach: infrastructure → memory system → agents → workflow → integration
- LangGraph StateGraph is used for the main workflow and complex orchestration (Emotion, Memory Save)
- Memory Evolution Engine integrates with Retrieval Engine to provide dynamic memory strength
- User Portrait is built from Reflections and used in response generation for personalization
- All memory access is tracked and used to reinforce frequently accessed memories
- Background jobs handle periodic memory evolution (forgetting curve application)
- Security features (encryption, PII masking) are implemented before deployment
- Context window management ensures LLM requests stay under 200,000 token limit
