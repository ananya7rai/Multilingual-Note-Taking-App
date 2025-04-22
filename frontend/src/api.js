
import axios from 'axios';


export const uploadAudio = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
  
    try {
      const response = await axios.post('http://localhost:8000/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      return response.data;
    } catch (error) {
      console.error('Error uploading audio:', error);
      throw error;
    }
  };
  

export const getSummary = async (transcript) => {
  try {
    const response = await axios.post('http://localhost:8000/summarize', {
      transcript: transcript,
    });
    return response.data;
  } catch (error) {
    console.error('Error summarizing text:', error);
    throw error;
  }
};

export const downloadPDF = async (meetingId) => {
  try {
    const response = await axios.get(`http://localhost:8000/export/${meetingId}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error downloading PDF:', error);
    throw error;
  }
};
