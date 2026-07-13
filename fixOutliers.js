const admin = require("firebase-admin");
const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
const db = admin.firestore();

// CONFIG
const USER_ID = "Nk64dxfaLOaxBjessyF8Tgifdt73";   // your real user ID
const THRESHOLD = 0.5; // 50% deviation allowed

// Compute total volume for an exercise
function computeVolume(sets) {
  return sets.reduce((sum, s) => sum + (s.reps * s.weight), 0);
}

async function fixOutliers() {
  const workoutsRef = db
    .collection("users")
    .doc(USER_ID)
    .collection("workouts");

  const snapshot = await workoutsRef.orderBy("date").get();
  const workouts = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }));

  // Track last valid sets per exercise
  let lastValidSets = {};

  for (const w of workouts) {
    const workoutId = w.id;
    const exercises = w;

    // Skip metadata fields
    const exerciseNames = Object.keys(exercises).filter(
      key => !["date", "workoutId", "workoutName"].includes(key)
    );

    for (const exercise of exerciseNames) {
      const setsToday = exercises[exercise];

      if (!Array.isArray(setsToday)) continue;

      const todayVolume = computeVolume(setsToday);

      if (!lastValidSets[exercise]) {
        // First time seeing this exercise
        lastValidSets[exercise] = setsToday;
        continue;
      }

      const lastSets = lastValidSets[exercise];
      const lastVolume = computeVolume(lastSets);

      // Compute deviation
      const deviation = Math.abs(todayVolume - lastVolume) / lastVolume;

      if (deviation > THRESHOLD) {
        console.log(
          `Outlier detected for ${exercise} in workout ${workoutId}: ${todayVolume} → fixing to ${lastVolume}`
        );

        // Adjust today's sets to match last valid reps/weights
        const adjustedSets = setsToday.map((set, index) => {
          const last = lastSets[index] || lastSets[lastSets.length - 1];
          return {
            reps: last.reps,
            weight: last.weight,
            completed: set.completed
          };
        });

        await workoutsRef.doc(workoutId).update({
          [exercise]: adjustedSets
        });
      } else {
        // Normal day → update last valid sets
        lastValidSets[exercise] = setsToday;
      }
    }
  }

  console.log("Per-exercise outlier correction complete.");
}

fixOutliers().catch(console.error);
