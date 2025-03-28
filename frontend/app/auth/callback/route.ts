import { NextResponse } from 'next/server'
// The client you created from the Server-Side Auth instructions
import { createClient } from '@/app/utils/supabase/server'

export async function GET(request: Request) {
  console.log("what")
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  // if "next" is in param, use it as the redirect URL
  const next = searchParams.get('next') ?? '/'


  if (code) {
    console.log("reached")
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      const forwardedHost = request.headers.get('x-forwarded-host') // original origin before load balancer

      console.log(forwardedHost, 2);
      const isLocalEnv = process.env.NODE_ENV === 'development'
      if (isLocalEnv) {
        // we can be sure that there is no load balancer in between, so no need to watch for X-Forwarded-Host
        console.log(process.env.NEXT_PUBLIC_SITE_URL, 1);
        await new Promise((r) => setTimeout(r, 1000));
        return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}${next}`)
      } else if (forwardedHost) {
        console.log(forwardedHost, 2);
        await new Promise((r) => setTimeout(r, 1000));
        return NextResponse.redirect(`https://${forwardedHost}${next}`)
      } else {
        console.log(process.env.NEXT_PUBLIC_SITE_URL, 3);
        await new Promise((r) => setTimeout(r, 1000));
        return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}${next}`)
      }
    }
  }

  // return the user to an error page with instructions
  return NextResponse.redirect(`${process.env.NEXT_PUBLIC_SITE_URL}/auth/auth-code-error`)
}