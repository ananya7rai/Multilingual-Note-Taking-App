from summarizer import summarize_text

transcript = """
So team, we’ve finalized the launch date for May 5th. Sarah will handle the outreach emails by Friday. 
Dev team must finish QA testing by next Wednesday. Also, we agreed to use the new brand colors from the design team. 
Next meeting is scheduled for May 1st.
"""

summary = summarize_text(transcript)
print(summary)
