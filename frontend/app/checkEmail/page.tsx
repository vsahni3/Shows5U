'use client';

import { Card, Flex, Heading, Text } from '@radix-ui/themes';

export default function CheckEmailPage() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      style={{ minHeight: '100vh' }}
    >
      <Card size="3" style={{ width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <Flex direction="column" gap="4" p="4">
          <Heading size="6">Check Your Email</Heading>
          <Text size="3" color="gray">
            We have sent you a confirmation email. Please verify your email address to continue.
          </Text>
        </Flex>
      </Card>
    </Flex>
  );
}
