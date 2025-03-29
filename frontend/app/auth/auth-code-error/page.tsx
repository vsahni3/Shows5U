'use client';

import { Card, Flex, Heading, Text } from '@radix-ui/themes';

export default function AuthError() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      style={{ minHeight: '100vh' }}
    >
      <Card size="3" style={{ width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <Flex direction="column" gap="4" p="4">
          <Heading size="6">NOOO</Heading>
          <Text size="3" color="gray">
            A very unforunate event occurred
          </Text>
        </Flex>
      </Card>
    </Flex>
  );
}
