import { decodeHex } from "@std/encoding/hex";

import "jsr:@std/dotenv/load";

import nacl from "tweetnacl";
import { createMiddleware } from "@hono/hono/factory";
import { HTTPException } from "@hono/hono/http-exception";
import { type Snowflake } from "discord-types";

export async function requestDiscord(
  endpoint: string | URL,
  options: RequestInit,
): Promise<Response> {
  const url = `https://discord.com/api/v10/${endpoint}`;

  const res = await fetch(url, {
    headers: {
      Authorization: `Bot ${Deno.env.get("DISCORD_TOKEN")}`,
      "Content-Type": "application/json; charset=UTF-8",
      "User-Agent":
        "DiscordBot (https://github.com/discord/discord-exmaple-app, 1.0.0)",
    },
    ...options,
  });

  if (!res.ok) {
    const data = await res.json();
    console.log(res.status);
    throw new Error(JSON.stringify(data));
  }

  // return original response
  return res;
}

export async function installGlobalCommands(
  appId: Snowflake,
  commands: BodyInit,
) {
  const endpoint = `applications/${appId}/commands`;

  try {
    await requestDiscord(endpoint, { method: "PUT", body: commands });
  } catch (err) {
    console.error(err);
  }
}

export function getRandomEmoji() {
  const emojiList = [
    "😭",
    "😄",
    "😌",
    "🤓",
    "😎",
    "😤",
    "🤖",
    "😶‍🌫️",
    "🌏",
    "📸",
    "💿",
    "👋",
    "🌊",
    "✨",
  ];
  return emojiList[Math.floor(Math.random() * emojiList.length)];
}

function concatUint8Array(...arrs: Uint8Array[]): Uint8Array {
  const totalLength = arrs.reduce((acc, e) => acc + e.length, 0);
  const buffer = new Uint8Array(totalLength);

  arrs.reduce((acc, elem) => {
    buffer.set(elem, acc);
    return acc + elem.length;
  }, 0);

  return buffer;
}

export const verifyDiscordMiddleware = (publicKey: string) => {
  return createMiddleware(async (c, next) => {
    const signature = c.req.header("X-Signature-Ed25519");
    const timestamp = c.req.header("X-Signature-Timestamp");

    if (!signature || !timestamp) {
      throw new HTTPException(401, { message: "Bad request" });
    }

    await next();

    const body = new Uint8Array(await c.req.arrayBuffer());
    const data = concatUint8Array(new TextEncoder().encode(timestamp), body);

    const valid = nacl.sign.detached.verify(
      data,
      decodeHex(signature),
      decodeHex(publicKey),
    );

    if (!valid) {
      throw new HTTPException(401, { message: "Bad request" });
    }
  });
};
