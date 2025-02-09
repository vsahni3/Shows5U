'use server';
import { createClient } from '@/app/utils/supabase/server';

import { revalidatePath } from 'next/cache'
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
    console.log(error)
    if (error) {
      redirect('/error')
    }
  
    revalidatePath('/', 'layout')
    redirect('/')
  }


export async function signup(formData: AuthData) {

    const supabase = await createClient()
    console.log('sing up');
    

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
    console.log(error)




    if (error) {
        redirect('/error')
    }
    

    revalidatePath('/', 'layout')
    redirect('/checkEmail')
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
  
    if (error) throw error
    
    if (data.url) {
      redirect(data.url)
    }
  }

