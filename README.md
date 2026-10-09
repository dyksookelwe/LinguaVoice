LinguaVoice: English to Slovak
An AI-powered application for dubbing English speech into Slovak while investigating methods for preserving the original speaker’s voice characteristics.
The project combines speech recognition, machine translation, voice synthesis, and audio processing in a web application. It also explores the trade-offs between voice similarity, speech quality, synchronization, processing speed, and cost.
Project Goal
The goal is to develop an application that transforms English-language audio recordings into Slovak speech while preserving the original meaning and, where technically feasible, recognizable characteristics of the original speaker’s voice.
The project focuses on integrating and evaluating existing AI technologies rather than training speech recognition or voice synthesis models from scratch.
Input
An English-language audio recording in MP3 or WAV format.
Initially, short recordings containing a single speaker and relatively clear speech.
Process
Audio validation and preprocessing.
Automatic speech recognition.
Speech segmentation and timestamp extraction.
English-to-Slovak translation.
Slovak speech synthesis using voice cloning or a standard TTS fallback.
Audio alignment, segment assembly, and export.
Output
A Slovak-language audio recording that can be played back and downloaded.
User Interface
The planned web application will support:
Audio upload and processing initiation.
Processing status and error reporting.
Display and editing of the recognized English transcript.
Display and editing of the Slovak translation.
Review and editing of individual speech segments.
Playback of generated segments where feasible.
Playback and download of the final audio.
Minimum Viable Product (MVP)
The MVP will focus on a complete English-to-Slovak audio dubbing workflow for short recordings containing a single speaker.
The initial version should support the following workflow:
Upload an English-language audio recording.
Validate and preprocess the input audio.
Generate an English transcript with timestamps or segment boundaries.
Translate the transcript into Slovak.
Allow the user to review and edit the transcript and translation.
Generate Slovak speech using voice cloning or voice adaptation where technically feasible, with a standard Slovak TTS solution as a fallback.
Allow the user to review and edit individual segments.
Regenerate audio for an edited segment.
Align and combine the generated segments into a single audio recording.
Play back and download the final audio through the web application.
MVP Scope
Included:
English audio input and Slovak audio output.
Single-speaker recordings.
Transcription, translation, and speech synthesis.
Basic segmentation and timestamp handling.
Text and segment editing.
Basic audio synchronization and export.
Public web deployment.
Error handling and input validation.
Automated tests for important processing components.
Documentation of the architecture, technology choices, and evaluation results.
Out of scope for the initial MVP:
Video input and video export.
Lip synchronization.
Multi-speaker detection and speaker-specific voice assignment.
Training custom speech recognition or voice synthesis models.
Advanced background music removal and source separation.
Professional-grade audio editing.
User accounts, subscriptions, and payment processing.
Support for arbitrary input and output languages.
These features may be considered after the core audio workflow has been validated.
Proposed Processing Pipeline
The following pipeline represents the current conceptual design. The exact implementation and technology choices will be determined through experimentation.
1. Audio Validation and Preprocessing
Validate the uploaded file, check its format and duration, and prepare the audio for downstream processing.
2. Automatic Speech Recognition (ASR)
Transcribe the English speech into text using a suitable speech recognition model or service.
3. Segmentation and Timestamping
Divide the transcript into manageable speech segments and associate them with their approximate positions in the original recording.
4. Translation
Translate the English transcript into Slovak while preserving meaning, context, and natural phrasing.
5. Voice Synthesis
Generate Slovak speech using a voice cloning or voice adaptation solution where feasible. If suitable cross-lingual voice preservation cannot be achieved, use a standard Slovak TTS solution.
6. Audio Alignment and Export
Adjust segment timing and, where appropriate, playback speed. Combine the generated segments into a single audio recording and export the result.
The pipeline may be revised if experimental results reveal a more suitable approach.
Candidate Technologies
The technologies listed below are candidates for evaluation, not final implementation decisions.
Pipeline Stage Candidate Technologies
Audio preprocessing FFmpeg, librosa
Speech recognition (ASR) faster-whisper, WhisperX, hosted ASR APIs
Segmentation and timestamping WhisperX, ASR timestamps, forced alignment
Translation Neural machine translation models, LLMs, translation APIs
Voice synthesis Commercial TTS and voice cloning APIs, multilingual local models
Audio synchronization Time stretching, segment-level timing adjustment, text adaptation
Audio assembly and export FFmpeg
Backend Python, FastAPI
Frontend React, TypeScript
Testing pytest, frontend testing tools
Deployment Container-based or managed web hosting
The final stack will be selected based on experimental results, integration requirements, and deployment constraints.
Technology Selection Criteria
Candidate technologies will be evaluated according to the following criteria:
Output quality: Naturalness, intelligibility, pronunciation, and overall dubbing quality.
Slovak language support: Actual quality of Slovak translation and speech synthesis, including cross-lingual voice cloning.
Voice similarity: The extent to which the generated speech retains recognizable characteristics of the original speaker.
Synchronization: Accuracy of segment boundaries and compatibility between original and generated speech duration.
Processing speed: Time required to process an audio recording and individual pipeline stages.
Cost: Estimated cost per processed recording, including repeated generation during editing.
Hardware requirements: CPU, GPU, memory, and storage requirements.
Integration complexity: Effort required to integrate the technology into the application.
Licensing: Compatibility with a public GitHub repository and the intended use of the application.
Deployment feasibility: Resource requirements, service limitations, reliability, and operational complexity.
The objective is to identify a practical combination of technologies that balances quality, cost, and implementation complexity.
Research Questions
1. Voice Generation and Cross-Lingual Voice Cloning
Can existing voice synthesis solutions generate natural-sounding Slovak speech while preserving recognizable characteristics of a speaker whose reference voice is in English?
The investigation will focus on:
Support for Slovak speech generation.
Cross-lingual voice cloning capabilities.
Similarity to the original speaker.
Slovak pronunciation and intelligibility.
Differences between cloned speech and standard Slovak TTS.
API limitations, licensing, and processing cost.
Voice cloning is a primary research objective, but the application must remain functional if the available solutions do not provide satisfactory results.
2. Speech Recognition and Translation
How accurately can existing ASR and translation solutions process short English-language recordings and produce reliable Slovak translations?
The investigation will focus on:
Recognition accuracy against reference transcripts.
Preservation of meaning during translation.
Natural Slovak phrasing.
Timestamp accuracy and segmentation quality.
Differences between local models and external APIs.
Processing speed and cost.
3. Audio Synchronization
How can generated Slovak speech be aligned with the timing of the original English speech?
The investigation will consider:
Segment-level duration differences.
Time stretching and playback speed adjustment.
Text adaptation for segments that are too long or too short.
Pauses and transitions between segments.
The trade-off between synchronization and speech naturalness.
Architecture Approach
The application will initially follow a modular architecture with separate frontend and backend components.
The backend will coordinate the dubbing workflow while keeping application API logic, AI provider integrations, and audio processing operations separated.
The architecture should support:
Replacing or comparing AI models and external services without extensive changes to the application.
Testing individual processing stages independently.
Handling processing failures and reporting status to the user.
Supporting transcript and segment editing.
Extending the application with additional audio and video processing capabilities.
The initial implementation will prioritize simplicity and maintainability. Additional infrastructure will be introduced only when justified by the selected technologies or application requirements.
Project Structure
The following structure is provisional and may change as the technology selection and implementation progress.
LinguaVoice/
├── README.md
├── .env.example
├── .gitignore
│
├── docs/
│   ├── architecture.md
│   ├── experiments.md
│   └── decisions.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── providers/
│   │   └── audio/
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   └── package.json
│
└── scripts/
    └── experiments/Main Components
Backend: Provides the application API and coordinates the dubbing workflow.
Frontend: Provides the user interface for uploading audio, reviewing and editing text, managing segments, and playing or downloading the generated audio.
Providers: Contains integrations with external APIs or local models for speech recognition, translation, and voice synthesis.
Audio Processing: Contains audio validation, preprocessing, synchronization, and export functionality.
Tests: Contains automated tests for individual components and end-to-end processing workflows.
Experiments: Contains scripts and supporting code used to evaluate candidate technologies.
Documentation: Records architectural decisions, experimental results, and implementation details.
The exact module boundaries and internal interfaces will be determined during implementation.
Deployment and Budget
The target is a publicly accessible web application that can be demonstrated without requiring users to install software locally.
Deployment choices will depend on the selected technologies, resource requirements, and hosting limitations. Heavy model inference may be delegated to external APIs or executed in a separate environment when appropriate.
The initial experimental budget is approximately €10–30.
Cost evaluation will consider:
Speech recognition and translation API usage.
Voice synthesis and voice cloning generation.
Repeated synthesis of edited segments.
Hosting and other required services.
The project will prioritize short test recordings, controlled experiments, and cost-effective solutions.
API keys and other secrets must be stored outside the source code. Uploaded audio and generated files should be handled with appropriate access controls and temporary file cleanup.
Learning Objectives
The project provides practical experience with:
Speech recognition and audio processing.
Machine translation and multilingual language technologies.
Voice synthesis and voice cloning.
Integration of AI models and external APIs.
Backend development with Python and FastAPI.
Frontend development for AI-powered applications.
API design and data contracts.
Audio segmentation, timing, and synchronization.
Automated testing and error handling.
Deployment and containerization.
Experimental evaluation and technical decision-making.
The project also aims to develop the ability to explain architectural decisions, justify technology selection, and evaluate the limitations of AI systems.
Project Roadmap
The project will be developed incrementally, progressing from technology research and feasibility testing to a functional audio dubbing application and further extensions.
Each phase defines objectives and expected deliverables. The scope and implementation order may be adjusted based on experimental results, technology limitations, and implementation complexity.
Status legend:
Planned
🟡 In Progress
Completed
⏸️ Deferred
Phase 1: Research and Technology Selection
Goal: Identify a feasible and cost-effective combination of technologies.
☐ Define functional and technical requirements for the MVP
☐ Prepare representative English audio samples for testing
☐ Evaluate speech recognition solutions for English audio
☐ Compare translation solutions for English-to-Slovak translation
☐ Investigate Slovak speech synthesis and cross-lingual voice cloning
☐ Test a standard Slovak TTS solution as a fallback
☐ Evaluate speech segmentation and timestamp extraction approaches
☐ Compare candidate technologies based on quality, cost, speed, hardware requirements, and integration complexity
☐ Review licensing restrictions and public usage requirements
☐ Evaluate deployment options and resource limitations
☐ Document experimental results and technology selection decisions
☐ Select the initial technology stack
Deliverable: A documented technology selection and a validated approach for building the initial audio dubbing pipeline.
Phase 2: Core Audio Processing Pipeline
Goal: Implement the complete audio processing workflow independently of the web interface.
☐ Implement audio file validation and format checks
☐ Implement audio preprocessing and format conversion where necessary
☐ Integrate automatic speech recognition (ASR)
☐ Extract speech segments and timestamps
☐ Integrate English-to-Slovak translation
☐ Define a consistent internal representation for transcripts and segments
☐ Integrate Slovak voice synthesis using the selected voice cloning or voice adaptation approach
☐ Implement a standard Slovak TTS fallback
☐ Implement basic duration adjustment and audio alignment
☐ Combine generated segments into a single audio recording
☐ Export the generated audio in a supported format
☐ Implement error handling for failed processing stages and external service failures
☐ Test the complete pipeline using short, single-speaker recordings
Deliverable: A working pipeline that converts English audio into downloadable Slovak audio.
Phase 3: MVP Web Application
Goal: Make the audio dubbing pipeline accessible through a public web application.
☐ Implement the frontend interface
☐ Implement audio upload and input validation
☐ Add processing initiation and job status tracking
☐ Display the recognized English transcript
☐ Display the Slovak translation
☐ Allow users to edit the transcript and translation
☐ Display individual speech segments and their timestamps
☐ Allow users to edit individual segments
☐ Support regenerating audio for an edited segment
☐ Add playback of individual generated segments where feasible
☐ Add playback of the final generated audio
☐ Implement audio file download
☐ Display processing errors and actionable feedback
☐ Connect the frontend to the backend API
☐ Deploy the application to a public environment
☐ Complete an end-to-end test using a single-speaker English recording
Deliverable: A publicly accessible web application supporting audio upload, transcription, translation, editing, synthesis, playback, and download.
Phase 4: Quality Evaluation and Optimization
Goal: Evaluate the generated dubbing and identify the limitations of the selected technologies.
☐ Evaluate speech recognition accuracy against reference transcripts
☐ Assess translation quality and meaning preservation
☐ Evaluate Slovak speech naturalness, pronunciation, and intelligibility
☐ Assess similarity between the generated voice and the original speaker
☐ Compare voice cloning results with the standard Slovak TTS fallback
☐ Measure processing time for individual pipeline stages
☐ Estimate the cost per processed audio file
☐ Evaluate timestamp accuracy and segment boundary quality
☐ Assess duration differences between original and generated speech
☐ Evaluate synchronization and segment transition quality
☐ Identify failure cases and document known limitations
☐ Optimize significant quality or performance bottlenecks
☐ Document experimental results and justify technology choices
Deliverable: A documented evaluation of the pipeline, including quality comparisons, cost estimates, limitations, and recommendations for improvement.
Phase 5: Reliability and Project Finalization
Goal: Make the application reliable, reproducible, and ready for public demonstration.
☐ Add unit tests for audio validation, segmentation, and other independent components
☐ Add integration tests for the main processing workflow
☐ Test invalid files, failed API calls, and incomplete processing jobs
☐ Implement file size and audio duration limits
☐ Verify temporary file handling and cleanup
☐ Ensure API keys and other secrets are not exposed
☐ Verify that the application operates within the available budget
☐ Finalize the public deployment configuration
☐ Containerize the application using Docker where appropriate
☐ Prepare installation and usage instructions
☐ Document the architecture and processing workflow
☐ Publish evaluation results and known limitations
☐ Review model and dependency licenses before public release
☐ Prepare a reproducible demonstration using a short audio sample
Deliverable: A stable, documented, publicly accessible MVP that can be demonstrated and evaluated without manual intervention from the developer.
Phase 6: Extended Audio Processing
Goal: Improve the quality and flexibility of audio dubbing beyond the initial MVP.
☐ Investigate noise reduction and audio restoration
☐ Investigate background music and speech separation
☐ Improve timing alignment between original and generated speech
☐ Explore text adaptation for segments that are too long or too short
☐ Improve handling of pauses and transitions between segments
☐ Add support for longer audio recordings
☐ Investigate multi-speaker detection and voice assignment
☐ Evaluate whether additional infrastructure is required for more complex processing workflows
Deliverable: An improved audio dubbing pipeline with additional capabilities validated through experiments.
Phase 7: Video Dubbing
Goal: Extend the application from audio dubbing to video dubbing.
☐ Add video file upload and validation
☐ Extract and preprocess audio from video files
☐ Preserve the original video timeline and relevant timing information
☐ Synchronize generated speech with the original video timeline
☐ Combine generated audio with the original video
☐ Export dubbed video in a supported format
☐ Investigate lip synchronization techniques
☐ Evaluate synchronization quality and processing requirements
Deliverable: A video dubbing workflow that builds on the validated audio processing pipeline.
Current Project Status
Current milestone: Research and MVP development.
Immediate priorities:
Verify the feasibility of Slovak voice synthesis that preserves recognizable characteristics of the original speaker.
Identify a reliable standard Slovak TTS fallback.
Validate the proposed ASR, translation, and segmentation approaches.
Confirm a feasible public deployment strategy.
Implement the first complete audio processing pipeline before investing heavily in the frontend.
The initial release will focus on short English-language audio recordings containing a single speaker. Video processing, multi-speaker support, advanced audio restoration, and other extended features will be considered after the core workflow has been validated.
The project will be considered successful when it provides a reproducible end-to-end audio dubbing workflow and documents the quality, cost, and limitations of the selected technologies.