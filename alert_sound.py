import streamlit as st
import base64

def play_alert_sound():
    # Generates a beep using HTML audio with a data URI (no file needed)
    beep_js = """
    <script>
    var context = new AudioContext();
    var oscillator = context.createOscillator();
    var gainNode = context.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(context.destination);
    oscillator.type = 'sine';
    oscillator.frequency.value = 880;
    gainNode.gain.setValueAtTime(1, context.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.8);
    oscillator.start(context.currentTime);
    oscillator.stop(context.currentTime + 0.8);
    </script>
    """
    st.components.v1.html(beep_js, height=0)
