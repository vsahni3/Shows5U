'use client';

import { Button, Card, Flex, Heading, TextField, Text } from '@radix-ui/themes';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { otpLogin, verifyOtp, signInWithGoogle } from "./actions"; // Ensure otpLogin is correctly imported
import { createClient } from '@/app/utils/supabase/client';  
import { useData } from '../context/dataContext';

export default function LoginPage() {
  const { setSharedData } = useData();
  const [step, setStep] = useState<'email' | 'otp'>('email');
  console.log(step)
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const supabase = createClient();
    
    async function signOutUser() {
      await supabase.auth.signOut();
      console.log("User signed out automatically on login page.");
      localStorage.clear();
      setSharedData({});
    }

    signOutUser();
  }, [setSharedData]);

  async function handleOtpLogin() {
    setLoading(true);
    setError('');

    try {
      const response = await otpLogin(email);
      if (response.success) {
        setStep('otp');
      } else {
        setError(response.message || 'Authentication failed. Please try again.');
      }
    } catch (error: unknown) {
      console.error('OTP login error:', error);
      setError('Unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const handleOtpSubmit = async (): Promise<void> => {
    setLoading(true);
    setError('');

    try {
      const response = await verifyOtp(email, otp);
      if (response.success) {
        router.push('/');
      } else {
        setError(response.message || 'OTP verification failed. Please try again.');
      }
    } catch (error: unknown) {
      console.error('OTP verification error:', error);
      setError('Unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      direction="column"
      gap="4"
      justify="center"
      align="center"
      style={{ minHeight: '100vh' }}
    >
      <Card size="3" style={{ width: '100%', maxWidth: '400px' }}>
        <Flex direction="column" gap="4" p="4">
          <Heading size="6" align="center" mb="4">
            Login
          </Heading>
          
          <form onSubmit={(e) => {
            e.preventDefault();
            if (step === 'email') {
              handleOtpLogin();
            } else {
              handleOtpSubmit();
            }
          }}>
            <Flex direction="column" gap="3">
            <TextField.Root
              type={step === 'email' ? 'email' : 'text'} // 'text' is appropriate for OTP input
              placeholder={step.charAt(0).toUpperCase() + step.slice(1)}
              value={step === 'email' ? email : otp}
              onChange={(e) => (step === 'email' ? setEmail(e.target.value) : setOtp(e.target.value))}
              required
            />

              {error && (
                <Text color="red" size="2" align="center">
                  {error}
                </Text>
              )}
  
              <Button type="submit" disabled={loading}>
                {step == 'email' ? (loading ? 'Sending OTP...' : 'Login') : (loading ? 'Verifying OTP...' : 'Verify OTP')}
              </Button>
            </Flex>
          </form>

          <Flex align="center" gap="3">
            <div style={{ flex: 1, height: '1px', background: 'var(--gray-5)' }} />
            <span style={{ color: 'var(--gray-11)' }}>or</span>
            <div style={{ flex: 1, height: '1px', background: 'var(--gray-5)' }} />
          </Flex>

          <Button onClick={signInWithGoogle} variant="outline">
            Continue with Google
          </Button>
        </Flex>
      </Card>
    </Flex>
  );
}
