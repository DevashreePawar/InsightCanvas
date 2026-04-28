import ExamplePrompts from '../components/ExamplePrompts';
import Footer from '../components/Footer';
import Hero from '../components/Hero';
import Impact from '../components/Impact';
import TechStack from '../components/TechStack';
import UseCases from '../components/UseCases';
import WorkspacePreview from '../components/WorkspacePreview';
import Workflow from '../components/Workflow';

export default function LandingPage() {
  return (
    <main>
      <Hero />
      <Workflow />
      <WorkspacePreview />
      <TechStack />
      <ExamplePrompts />
      <UseCases />
      <Impact />
      <Footer />
    </main>
  );
}
