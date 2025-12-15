# Multi-AI Chat Interface

A Streamlit-based application that demonstrates concurrent interaction with multiple AI language models. This project was developed as part of my learning journey to understand modern AI APIs, real-time web applications, and Python development best practices.

![Multi-AI Chat Interface](screenshot.png) <!-- You can add a screenshot of your application here -->

## Project Overview

This application allows users to simultaneously interact with three different AI models:
- Google's Gemini
- OpenAI's GPT models

Each model runs in its own column with message history, enabling real-time comparison of responses across different AI providers.

## Learning Objectives

This project helped me gain hands-on experience with:

1. **Modern AI APIs**
   - Integration with multiple AI providers (Google, OpenAI)
   - Handling API authentication and rate limiting
   - Managing asynchronous API responses for parallel processing

2. **Streamlit Framework**
   - Building interactive web applications
   - Real-time updates and state management
   - Custom styling and layout design
   - Component containerization (using `st.container`)

3. **Python Development**

   - API client libraries (google-generativeai, openai)
   - Async/await patterns (using `asyncio`)
   - Error handling and logging

4. **UI/UX Design**
   - Responsive layouts
   - Message containment and scrolling
   - Visual feedback and loading states
   - Cross-model interaction patterns

## Technical Implementation

### Key Features
- **Parallel Processing**: Queries all AI models simultaneously using `asyncio`, significantly reducing wait time.
- **Three-column Layout**: Independent scrollable chat containers for each model.
- **Efficient Caching**: Caches model lists to avoid unnecessary API calls.
- **Real-time Updates**: Smooth user experience with instant feedback.
- **Secure API Key Management**: Configuration stored locally in `config.json`.

### Libraries Used
- `streamlit`: Web application framework
- `google-generativeai`: Google's Gemini API client

- `asyncio`: Asynchronous I/O handling
- `watchdog`: File system monitoring (for development)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multi-ai-chat.git
   cd multi-ai-chat
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## Configuration

The application uses a **Bring Your Own Key (BYOK)** approach.

1. Create a `config.json` file in the root directory:
   ```json
   {
       "gemini_key": "YOUR_GEMINI_API_KEY",
       "openai_key": "YOUR_OPENAI_API_KEY",
       "custom_providers": []
   }
   ```
2. Launch the application.

## Future Improvements

- [ ] Add conversation export functionality
- [ ] Implement conversation history persistence
- [ ] Add more granular model settings
- [ ] Enhance error handling and user feedback
- [ ] Add message threading capabilities

## Contributing

While this is a personal learning project, suggestions and feedback are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Streamlit team for their excellent documentation
- The AI provider communities for their comprehensive APIs
- Various online tutorials and resources that helped in learning

---
*This project is part of my portfolio demonstrating practical experience with modern web development, AI integration, and Python programming.*
