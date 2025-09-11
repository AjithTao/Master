# AI Setup Guide for Leadership Quality Tool

## Overview

The Leadership Quality Tool includes advanced AI features powered by OpenAI for natural language processing, intelligent query understanding, and enhanced responses. This guide explains how to set up and configure these features.

## Features

When properly configured with OpenAI, the tool provides:

- **Natural Language Understanding**: Ask questions in plain English like "What is Ashwin working on?" or "Show me CCM project details"
- **Intelligent JQL Generation**: Automatically converts natural language to proper Jira Query Language (JQL)
- **Contextual Responses**: AI-powered responses that understand context and provide leadership insights
- **Enhanced Query Processing**: Better understanding of project names, assignees, and issue types

## Setup Instructions

### 1. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Click "Create new secret key"
5. Copy the generated key (starts with `sk-`)

### 2. Configure the Backend

1. Navigate to the `backend` directory
2. Copy the template file:
   ```bash
   cp config.env.template config.env
   ```
3. Edit `config.env` and replace the placeholder with your actual API key:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

### 3. Restart the Application

After configuring the API key:

1. Stop the current application (Ctrl+C if running)
2. Restart using `start.bat` or your preferred method
3. The backend will now load the OpenAI configuration

## Verification

To verify the AI features are working:

1. Open the frontend at http://localhost:3000
2. Try asking natural language questions in the chat:
   - "What is CCM-283?"
   - "Show me CCM project details"
   - "Who is working on CCM project?"

### Expected Behavior

**With OpenAI configured:**
- Natural language queries are understood and converted to proper JQL
- Responses include intelligent summaries and leadership insights
- Context is maintained across conversation

**Without OpenAI (fallback mode):**
- Basic keyword matching for projects, assignees, and issue types
- Simpler responses with clear formatting
- Note displayed about configuring OpenAI for better features

## Troubleshooting

### Common Issues

1. **"No OpenAI API key found"**
   - Ensure `config.env` file exists in the `backend` directory
   - Verify the API key is set correctly
   - Restart the backend server

2. **"OpenAI API key is placeholder"**
   - Replace the placeholder value with your actual API key
   - Make sure the key starts with `sk-`

3. **API Key Invalid**
   - Verify the key is copied correctly (no extra spaces)
   - Check that the key is active in your OpenAI dashboard
   - Ensure you have credits/usage available

### Logs

Check the backend logs for AI-related messages:
- `Intelligent AI Engine initialized with OpenAI` - Success
- `No OpenAI API key found - AI features will be limited` - Need configuration

## Cost Considerations

- The tool uses `gpt-4o-mini` model by default (cost-effective)
- Typical usage: ~$0.001-0.01 per query depending on complexity
- Monitor usage in your OpenAI dashboard

## Security Notes

- Never commit `config.env` to version control
- Keep your API key secure and private
- The template file (`config.env.template`) is safe to commit
- Consider using environment variables in production deployments

## Support

If you encounter issues:
1. Check the backend logs for error messages
2. Verify your OpenAI account has available credits
3. Test with simple queries first
4. Ensure Jira integration is working before testing AI features
