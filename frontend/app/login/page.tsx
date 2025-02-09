'use client';


import { Button, Card, Flex, Heading, TextField } from '@radix-ui/themes';
import { useState, useEffect } from 'react';
import { redirect, useRouter } from 'next/navigation';
import { login, signup, signInWithGoogle } from "./actions";
import { createClient } from '@/app/utils/supabase/client';  // Add this import

export default function LoginPage() {

    useEffect(() => {
        const supabase = createClient();
        
        async function signOutUser() {
            await supabase.auth.signOut();
            console.log("User signed out automatically on login page.");
        }

        signOutUser();
    }, []);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleGoogleLogin() {
    try {
      await signInWithGoogle()
    } catch (error) {
      console.error('Google auth error:', error)
    }
  }
    


  async function handleAuth(event: React.MouseEvent<HTMLButtonElement, MouseEvent>, isSignup: boolean) {

    event.preventDefault();
    setLoading(true);
  

  
    if (isSignup) {
      await signup({ email, password });
    } else {
      await login({ email, password });
    }
  
    setLoading(false);
    router.push("/");
  }
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
          
          <form>
            <Flex direction="column" gap="3">
              <TextField.Root
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />

              
              <TextField.Root
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
  
              <Button onClick={(e) => handleAuth(e, false)} disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </Button>
              <Button onClick={(e) => handleAuth(e, true)} disabled={loading}>
                {loading ? 'Signing up...' : 'Sign up'}
              </Button>
            </Flex>
          </form>

          <Flex align="center" gap="3">
            <div style={{ flex: 1, height: '1px', background: 'var(--gray-5)' }} />
            <span style={{ color: 'var(--gray-11)' }}>or</span>
            <div style={{ flex: 1, height: '1px', background: 'var(--gray-5)' }} />
          </Flex>

          <Button onClick={handleGoogleLogin} variant="outline">
            Continue with Google
          </Button>
        </Flex>
      </Card>
    </Flex>
  );
}
