const admin = require("firebase-admin");
const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
const db = admin.firestore();

// CONFIG
const USER_ID = "6LQ3KJW8rJfUlmwmEEvpWEJBXwk2";
const MULTIPLIER = 3; // Outlier threshold

async function fixOutliers() {
  const workoutsRef = db.collection("users").doc(USER_ID).collection("workouts");
  const snapshot = await workoutsRef.orderBy("date").get();

  const workouts = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }));

  let lastValidVolumeByExercise = {};

  for (const w of workouts) {
    const exercise = w.exerciseName;
    const volume = w.totalVolume;

    if (!lastValidVolumeByExercise[exercise]) {
      lastValidVolumeByExercise[exercise] = volume;
      continue;
    }

    const lastValid = lastValidVolumeByExercise[exercise];

    if (volume > lastValid * MULTIPLIER) {
      console.log(`Outlier detected in ${exercise} on ${w.date}: ${volume} → fixing to ${lastValid}`);

      await workoutsRef.doc(w.id).update({
        totalVolume: lastValid
      });
    } else {
      lastValidVolumeByExercise[exercise] = volume;
    }
  }

  console.log("Outlier correction complete.");
}

fixOutliers().catch(console.error);
