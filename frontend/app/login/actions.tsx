'use server';
import { createClient } from '@/app/utils/supabase/server';

import { redirect } from 'next/navigation'

type AuthData = {
  email: string;
  password: string;
}

export async function login(formData: AuthData) {
    const supabase = await createClient()


    // type-casting here for convenience
    // in practice, you should validate your inputs

    await supabase.auth.signOut();
    const { error } = await supabase.auth.signInWithPassword(formData)

    if (error) {
      return { success: false, message: error.message }; // ✅ Return a structured response
    }
  
    return { success: true };
  

  }


export async function signup(formData: AuthData) {

    const supabase = await createClient()
    

    // type-casting here for convenience
    // in practice, you should validate your inputs

    await supabase.auth.signOut();
    const { error } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
            emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`, // 🔹 Ensures redirect after email confirmation
        },
    });





    if (error) {
      return { success: false, message: error.message }; // ✅ Return a structured response
    }
  
    return { success: true };
    

}


export async function signInWithGoogle() {
    const supabase = await createClient()
    console.log(process.env.NEXT_PUBLIC_SITE_URL, 99);
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
      console.log('happened')
      console.log(data.url)
      redirect(data.url)
    }
    return { success: true };
  }

