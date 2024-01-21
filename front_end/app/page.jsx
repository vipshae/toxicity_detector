import InputTextBox from './ui/input-text-box';
import Image from 'next/image';

function Header({ title }) {
    return <h1>{title ? title: 'Hold on'}</h1>;
}

export default function Home() {    
    return(
        <main>
            <div>
                <Header title="Toxicity predictor" /> 
                <InputTextBox></InputTextBox>
                {/* <Image
                    src="happy.svg"
                    width={100}
                    height={76}
                    className="hidden md:block"
                    alt="default emotion"
                /> */}
            </div>
        </main>
    );
}