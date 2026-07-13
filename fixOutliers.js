const admin = require("firebase-admin");
const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
const db = admin.firestore();

const USER_ID = "Nk64dxfaLOaxBjessyF8Tgifdt73";
const SET_THRESHOLD = 0.2; // 20% deviation allowed

function isSetOutlier(today, last) {
  const repsDev = Math.abs(today.reps - last.reps) / last.reps;
  const weightDev = Math.abs(today.weight - last.weight) / last.weight;
  return repsDev > SET_THRESHOLD || weightDev > SET_THRESHOLD;
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

      if (!lastValidSets[exercise]) {
        lastValidSets[exercise] = todaySets;
        continue;
      }

      const lastSets = lastValidSets[exercise];

      let changed = false;
      const adjustedSets = todaySets.map((set, index) => {
        const last = lastSets[index] || lastSets[lastSets.length - 1];

        if (isSetOutlier(set, last)) {
          changed = true;
          return {
            reps: last.reps,
            weight: last.weight,
            completed: set.completed
          };
        }

        return set;
      });

      if (changed) {
        console.log(
          `Adjusted ${exercise} in workout ${workoutId} (per-set correction)`
        );

        await workoutsRef.doc(workoutId).update({
          [exercise]: adjustedSets
        });
      } else {
        lastValidSets[exercise] = todaySets;
      }
    }
  }

  console.log("Per-exercise set-level correction complete.");
}

fixOutliers().catch(console.error);
