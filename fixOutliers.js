const admin = require("firebase-admin");
const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
const db = admin.firestore();

const USER_ID = "Nk64dxfaLOaxBjessyF8Tgifdt73";
const VOLUME_THRESHOLD = 0.3; // 30% deviation allowed

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

  let lastValidSets = {};

  for (const w of workouts) {
    const workoutId = w.id;

    const exerciseNames = Object.keys(w).filter(
      key => !["date", "workoutId", "workoutName"].includes(key)
    );

    for (const exercise of exerciseNames) {
      const todaySets = w[exercise];
      if (!Array.isArray(todaySets)) continue;

      const todayVolume = computeVolume(todaySets);

      if (!lastValidSets[exercise]) {
        lastValidSets[exercise] = todaySets;
        continue;
      }

      const lastSets = lastValidSets[exercise];
      const lastVolume = computeVolume(lastSets);

      const deviation = Math.abs(todayVolume - lastVolume) / lastVolume;

      if (deviation > VOLUME_THRESHOLD) {
        console.log(
          `OUTLIER: ${exercise} in workout ${workoutId} — ${todayVolume} vs ${lastVolume}`
        );

        const adjustedSets = todaySets.map((set, index) => {
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
        lastValidSets[exercise] = todaySets;
      }
    }
  }

  console.log("Outlier correction complete.");
}

fixOutliers().catch(console.error);
