import { Flex, Heading, Button } from "@radix-ui/themes";
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
const Header = ({ isLoading }) => {
  const router = useRouter();
  return (
    <Flex
      justify="between"
      align="center"
      className="bg-white w-full px-8 py-3 fixed top-0 left-0 right-0 shadow-sm z-10"
    >
      {/* Logo and Nav Links */}
      <Flex align="center" gap="4">
        <Image
          src="/luffy.png"
          alt="Logo"
          className="w-16 h-16 object-contain object-cover rounded-full"
        />
        <Link href='/'>
        <Heading size="4" className="text-gray-700 font-medium">
          Shows5U
        </Heading>
        </Link>
        <Link href='/personal'>
        <Heading size="4" className="text-gray-700 font-medium">
          Personal
        </Heading>
        </Link>
      </Flex>

      {/* Sign Out Button */}
      <Button
        disabled={isLoading}
        onClick={() => router.push('/login')}
        variant="soft"
        className="px-4 py-2 text-sm rounded-md bg-neutral-100 hover:bg-neutral-200 transition-colors"
      >
        Sign Out
      </Button>
    </Flex>
  );
};

export default Header;
