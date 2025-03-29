import { NextResponse } from 'next/server';
import { createClient } from '@/app/utils/supabase/server';

export async function GET(request: Request) {
  console.log(request.url)
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/';


  const supabase = await createClient();

  if (code) {
    // Handle OAuth (e.g., Google) authentication callback
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (error) {
      console.error('OAuth exchange error:', error.message);
      return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}/auth/auth-code-error`);
    }
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}${next}`);
  } 

  // If no recognizable authentication parameters are present
  return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}/auth/auth-code-error`);
}
