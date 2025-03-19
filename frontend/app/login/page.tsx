'use client';


import { Button, Card, Flex, Heading, TextField, Text } from '@radix-ui/themes';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { login, signup, signInWithGoogle } from "./actions";
import { createClient } from '@/app/utils/supabase/client';  
import { useData } from '../context/dataContext';


export default function LoginPage() {
  const { setSharedData } = useData();

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

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleAuthAction<T = void>(
    authFunction: (args: T) => Promise<{ success: boolean; message?: string }>,
    args?: T 
  ) {
    let success = true;
    setLoading(true);
    

    try {
      let response;
      if (args !== undefined) {
        response = await authFunction(args);
      } else {
        response = await (authFunction as () => Promise<{ success: boolean; message?: string }>)();
      }
  
      if (!response.success) {
        success = false;
        setError(response.message || "Authentication failed. Please try again.");
        return; // ⛔ Stop execution if login/signup fails
      }
      
    } catch (error: unknown) {
      success = false;
      console.error("Auth error:", error);
      setError("Unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
      return success;
    }
  
  }

    


  async function handleAuth(isSignup: boolean) {
    let success;
    if (isSignup) {
      success = await handleAuthAction(signup, { email, password });
      console.log(success)
      if (success) router.push("/checkEmail");
    } else {
      success = await handleAuthAction(login, { email, password });
      if (success) router.push("/");
    }
    
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

                  {error && (
                  <Text color="red" size="2" align="center">
                      {error}
                  </Text>
              )}
  
              <Button onClick={() => handleAuth(false)} disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </Button>
              <Button onClick={() => handleAuth(true)} disabled={loading}>
                {loading ? 'Signing up...' : 'Sign up'}
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





