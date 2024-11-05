import "jsr:@std/dotenv/load";

import {
  ApplicationCommandType,
  ApplicationIntegrationType,
  InteractionContextType,
} from "discord-types";
import { installGlobalCommands } from "./utils.ts";

const TEST_COMMAND = {
  name: "test",
  description: "Basic command",
  type: ApplicationCommandType.ChatInput,
  integration_types: [
    ApplicationIntegrationType.GuildInstall,
    ApplicationIntegrationType.UserInstall,
  ],
  contexts: [
    InteractionContextType.Guild,
    InteractionContextType.BotDM,
    InteractionContextType.PrivateChannel,
  ],
};

const PIN_MESSAGE_COMMAND = {
  name: "pin",
  type: ApplicationCommandType.Message,
  integration_types: [ApplicationIntegrationType.GuildInstall],
  contexts: [
    InteractionContextType.Guild,
    InteractionContextType.PrivateChannel,
  ],
};

const UNPIN_MESSAGE_COMMAND = {
  name: "pin",
  type: ApplicationCommandType.Message,
  integration_types: [ApplicationIntegrationType.GuildInstall],
  contexts: [
    InteractionContextType.Guild,
    InteractionContextType.PrivateChannel,
  ],
};

const ALL_COMMANDS = [TEST_COMMAND, PIN_MESSAGE_COMMAND, UNPIN_MESSAGE_COMMAND];

if (import.meta.main) {
  const appId = Deno.env.get("APP_ID");
  if (appId) {
    installGlobalCommands(appId, JSON.stringify(ALL_COMMANDS));
  }
}