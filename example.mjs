import OpenAI from "openai";
import "dotenv/config";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function main() {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: "Write a haiku about recursion in programming." },
      ],
    });

    console.log(completion.choices[0].message.content);
  } catch (error) {
    console.error("Erreur lors de la requête API :", error);
  }
}

main();