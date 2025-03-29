'use server';
import { createClient } from '@/app/utils/supabase/server';

import { redirect } from 'next/navigation'

export async function otpLogin(email: string): Promise<{ success: boolean; message?: string }> {
  const supabase = await createClient();

  // Ensure the email is provided
  if (!email) {
    return { success: false, message: 'Email is required.' };
  }

  // Sign out any existing session
  await supabase.auth.signOut();

  // Send OTP to the user's email
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      shouldCreateUser: true, // Set to false to prevent automatic user creation
      emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
    },
  });

  if (error) {
    return { success: false, message: error.message };
  }

  return { success: true };
}


export async function verifyOtp(email: string, token: string): Promise<{ success: boolean; message?: string }> {
  const supabase = await createClient();

  if (!email || !token) {
    return { success: false, message: 'Email and OTP are required.' };
  }

  const { error } = await supabase.auth.verifyOtp({
    email,
    token,
    type: 'email', // required for email-based OTP
  });

  if (error) {
    return { success: false, message: error.message };
  }

  return { success: true };
}


export async function signInWithGoogle() {
    const supabase = await createClient()
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    })
  
    if (error) {
      return { success: false, message: error.message }; // ✅ Return a structured response
    }
  
    
    
    if (data.url) {
      redirect(data.url)
    }
    return { success: true };
  }

