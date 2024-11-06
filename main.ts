import "jsr:@std/dotenv/load";

import { Hono } from "@hono/hono";
import { InteractionResponseType, InteractionType } from "discord-interactions";
import { getRandomEmoji, verifyDiscordMiddleware } from "./utils.ts";
import {
  type APIApplicationCommandInteractionData,
  type APIContextMenuInteractionData,
  APIMessage,
  type APIMessageApplicationCommandInteractionData,
  type APIMessageApplicationCommandInteractionDataResolved,
  MessageFlags,
  Utils,
} from "discord-types";
import { requestDiscord } from "./utils.ts";

const PORT: number = Number(Deno.env.get("PORT")) || 3000;
const PUBLIC_KEY: string = Deno.env.get("PUBLIC_KEY") || "";

const app = new Hono();

app.use("/interactions", verifyDiscordMiddleware(PUBLIC_KEY));

app.post("/interactions", async (c) => {
  const body = await c.req.json();

  const interaction = body;
  const { "type": type_, data }: {
    data: APIApplicationCommandInteractionData;
    "type": InteractionType;
  } = interaction;

  if (type_ === InteractionType.PING) {
    return c.json({ "type": InteractionResponseType.PONG });
  }

  if (type_ === InteractionType.APPLICATION_COMMAND) {
    const { name } = data;

    if (name === "test") {
      return c.json({
        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data: {
          content: `hello world ${getRandomEmoji()}`,
        },
      });
    }

    if (Utils.isApplicationCommandGuildInteraction(interaction)) {
      if (Utils.isContextMenuApplicationCommandInteraction(interaction)) {
        if (name === "pin") {
          console.log("Pin interaction");

          const resolvedData = interaction.data
            ?.resolved as APIMessageApplicationCommandInteractionDataResolved;

          if (resolvedData) {
            const message = Object.values(
              resolvedData?.messages,
            )[0] as APIMessage;
            const messageId = message.id;
            const channelId = message.channel_id;
            const endpoint = `channels/${channelId}/pins/${messageId}`;
            try {
              const result = await requestDiscord(endpoint, { method: "PUT" });
              return c.json({
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                data: {
                  content: `Pin message`,
                  flags: MessageFlags.Ephemeral,
                },
              });
            } catch (err) {
              console.error(err);
            }
          }
        }
        if (name === "unpin") {
          console.log("Unpin interaction");

          const resolvedData = interaction.data
            ?.resolved as APIMessageApplicationCommandInteractionDataResolved;

          if (resolvedData) {
            const message = Object.values(
              resolvedData?.messages,
            )[0] as APIMessage;
            const messageId = message.id;
            const channelId = message.channel_id;
            const endpoint = `channels/${channelId}/pins/${messageId}`;
            try {
              const result = await requestDiscord(endpoint, {
                method: "DELETE",
              });
              if (result.ok) {
                return c.json({
                  "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                  data: {
                    content: "Unpin message",
                  },
                });
              } else {
                return c.json({
                  "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                  data: {
                    content: "Failed unpin message",
                    flags: MessageFlags.Ephemeral,
                  },
                });
              }
            } catch (err) {
              console.error(err);
              return c.json({
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                data: {
                  content: "Failed unpin message",
                  flags: MessageFlags.Ephemeral,
                },
              });
            }
          }
        }
      }
    }
  }

  console.error("unknown interaction type");

  c.status(400);
  return c.json({ error: "unknown interaction tpye" });
});

Deno.serve({ port: PORT }, app.fetch);

// Learn more at https://docs.deno.com/runtime/manual/examples/module_metadata#concepts
// if (import.meta.main) {
//   Deno.serve({ port: PORT }, app.fetch);
// }
